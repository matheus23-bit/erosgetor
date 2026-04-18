"""
ErosGest AI v2 — Database com sistema de usuários e permissões
"""
import sqlite3
import json
import logging
import base64
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)
DB_PATH = Path.home() / ".erosgest" / "erosgest.db"

def get_db_path():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return str(DB_PATH)

@contextmanager
def get_connection():
    conn = sqlite3.connect(get_db_path(), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn; conn.commit()
    except Exception:
        conn.rollback(); raise
    finally:
        conn.close()

ROLES = {
    "master":      {"label":"Dono/Master",   "level":4},
    "gerente":     {"label":"Gerente",        "level":3},
    "supervisor":  {"label":"Supervisor",     "level":2},
    "funcionario": {"label":"Funcionário",    "level":1},
}

DEFAULT_PERMISSIONS = {
    "master":      {"dashboard":True,"products":True,"sales":True,"finance":True,
                    "assistant":True,"settings":True,"delete_product":True,
                    "edit_product":True,"manage_users":True,"view_metrics":True},
    "gerente":     {"dashboard":True,"products":True,"sales":True,"finance":True,
                    "assistant":True,"settings":False,"delete_product":True,
                    "edit_product":True,"manage_users":False,"view_metrics":True},
    "supervisor":  {"dashboard":True,"products":True,"sales":True,"finance":False,
                    "assistant":True,"settings":False,"delete_product":False,
                    "edit_product":True,"manage_users":False,"view_metrics":False},
    "funcionario": {"dashboard":True,"products":False,"sales":True,"finance":False,
                    "assistant":False,"settings":False,"delete_product":False,
                    "edit_product":False,"manage_users":False,"view_metrics":False},
}

def init_database():
    with get_connection() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS config(
                key TEXT PRIMARY KEY, value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
                full_name TEXT DEFAULT '', role TEXT DEFAULT 'funcionario',
                active INTEGER DEFAULT 1, custom_permissions TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_login TIMESTAMP);
            CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, ean TEXT DEFAULT '', category TEXT DEFAULT '',
                supplier TEXT DEFAULT '', cost_price REAL DEFAULT 0,
                sale_price REAL DEFAULT 0, quantity INTEGER DEFAULT 0,
                min_quantity INTEGER DEFAULT 5, unit TEXT DEFAULT 'un',
                image_url TEXT DEFAULT '', product_url TEXT DEFAULT '',
                notes TEXT DEFAULT '', active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS sales(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER REFERENCES products(id),
                product_name TEXT NOT NULL, quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL, total_price REAL NOT NULL,
                cost_price REAL DEFAULT 0, profit REAL DEFAULT 0,
                payment_method TEXT DEFAULT 'dinheiro', tax_amount REAL DEFAULT 0,
                user_id INTEGER REFERENCES users(id), customer_name TEXT DEFAULT '',
                notes TEXT DEFAULT '', sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT NOT NULL,
                amount REAL NOT NULL, category TEXT DEFAULT 'outros',
                payment_method TEXT DEFAULT '',
                expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, notes TEXT DEFAULT '');
            CREATE TABLE IF NOT EXISTS price_history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER REFERENCES products(id),
                source TEXT, price REAL, url TEXT,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS gamification(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                milestone_type TEXT, milestone_value INTEGER, user_id INTEGER,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
            CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
        """)
        for k,v in {
            "store_name":"Minha Loja","tax_regime":"simples_nacional",
            "simples_rate":"0.04","icms_rate":"0.12","state":"SP",
            "openai_api_key":"","serpapi_key":"","assemblyai_key":"",
            "default_margin":"0.30","low_stock_alert":"5",
            "theme":"dark","worker_interval":"600","tts_enabled":"1",
        }.items():
            c.execute("INSERT OR IGNORE INTO config(key,value) VALUES(?,?)",(k,v))
        if not c.execute("SELECT id FROM users WHERE role='master'").fetchone():
            import hashlib
            pw = hashlib.sha256("admin123".encode()).hexdigest()
            c.execute("INSERT OR IGNORE INTO users(username,password_hash,full_name,role) VALUES('admin',?,'Administrador','master')",(pw,))

def hash_pw(pw):
    import hashlib; return hashlib.sha256(pw.encode()).hexdigest()

def authenticate(username, password):
    with get_connection() as c:
        row = c.execute("SELECT * FROM users WHERE username=? AND active=1",(username,)).fetchone()
        if not row or row["password_hash"]!=hash_pw(password): return None
        c.execute("UPDATE users SET last_login=? WHERE id=?",(datetime.now(),row["id"]))
        return dict(row)

def get_user_permissions(user):
    role = user.get("role","funcionario")
    base = DEFAULT_PERMISSIONS.get(role, DEFAULT_PERMISSIONS["funcionario"]).copy()
    try:
        custom = json.loads(user.get("custom_permissions") or "{}")
        base.update(custom)
    except Exception: pass
    return base

def can(user, action):
    if not user: return False
    return get_user_permissions(user).get(action, False)

def get_all_users():
    with get_connection() as c:
        return [dict(r) for r in c.execute("SELECT * FROM users ORDER BY role,username").fetchall()]

def create_user(username, password, full_name, role, actor):
    if not can(actor,"manage_users"): raise PermissionError("Sem permissão")
    if role=="master": raise ValueError("Não pode criar outro Master")
    with get_connection() as c:
        c.execute("INSERT INTO users(username,password_hash,full_name,role) VALUES(?,?,?,?)",
                  (username,hash_pw(password),full_name,role))

def update_user_role(target_id, new_role, actor):
    if not can(actor,"manage_users"): raise PermissionError("Sem permissão")
    if new_role=="master": raise ValueError("Não pode promover para Master")
    with get_connection() as c:
        c.execute("UPDATE users SET role=? WHERE id=? AND role!='master'",(new_role,target_id))

def update_user_permissions(target_id, perms_dict, actor):
    if not can(actor,"manage_users"): raise PermissionError("Sem permissão")
    with get_connection() as c:
        c.execute("UPDATE users SET custom_permissions=? WHERE id=? AND role!='master'",
                  (json.dumps(perms_dict),target_id))

def toggle_user_active(target_id, actor):
    if not can(actor,"manage_users"): raise PermissionError("Sem permissão")
    with get_connection() as c:
        c.execute("UPDATE users SET active=1-active WHERE id=? AND role!='master'",(target_id,))

def get_config(key, default=None):
    with get_connection() as c:
        r=c.execute("SELECT value FROM config WHERE key=?",(key,)).fetchone()
        return r[0] if r else default

def set_config(key, value):
    with get_connection() as c:
        c.execute("INSERT OR REPLACE INTO config(key,value,updated_at) VALUES(?,?,?)",
                  (key,value,datetime.now()))

def get_all_config():
    with get_connection() as c:
        return {r[0]:r[1] for r in c.execute("SELECT key,value FROM config").fetchall()}

def add_product(name, cost_price, sale_price, quantity, category="",
                supplier="", ean="", unit="un", notes="", image_url="", product_url="", image_data=None):
    with get_connection() as c:
        # Se image_data (bytes) for fornecido, codifica para base64 e salva
        if image_data:
            import base64
            image_url = "data:image/png;base64," + base64.b64encode(image_data).decode('utf-8')
        
        cur=c.execute("""INSERT INTO products(name,ean,category,supplier,cost_price,sale_price,
            quantity,unit,notes,image_url,product_url) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (name,ean,category,supplier,cost_price,sale_price,quantity,unit,notes,image_url,product_url))
        return cur.lastrowid

def update_product(pid, **kw):
    allowed={"name","ean","category","supplier","cost_price","sale_price",
             "quantity","unit","notes","active","min_quantity","image_url","product_url"}
    kw={k:v for k,v in kw.items() if k in allowed}
    if not kw: return
    kw["updated_at"]=datetime.now().isoformat()
    with get_connection() as c:
        c.execute(f"UPDATE products SET {', '.join(f'{k}=?' for k in kw)} WHERE id=?",
                  list(kw.values())+[pid])

def get_products(active_only=True, category=None, low_stock=False):
    with get_connection() as c:
        q="SELECT * FROM products WHERE 1=1"; p=[]
        if active_only: q+=" AND active=1"
        if category: q+=" AND category=?"; p.append(category)
        if low_stock: q+=" AND quantity<=min_quantity"
        return [dict(r) for r in c.execute(q+" ORDER BY name",p).fetchall()]

def record_sale(product_id, product_name, quantity, unit_price, cost_price,
                payment_method="dinheiro", user_id=None, customer_name="", notes=""):
    total=unit_price*quantity; profit=(unit_price-cost_price)*quantity
    tax=total*float(get_config("simples_rate","0.04"))
    with get_connection() as c:
        if product_id:
            prod=c.execute("SELECT quantity FROM products WHERE id=?",(product_id,)).fetchone()
            if prod and prod[0]<quantity: raise ValueError(f"Estoque insuficiente: {prod[0]} disponível")
        cur=c.execute("""INSERT INTO sales(product_id,product_name,quantity,unit_price,total_price,
            cost_price,profit,payment_method,tax_amount,user_id,customer_name,notes)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (product_id,product_name,quantity,unit_price,total,cost_price,profit,
             payment_method,tax,user_id,customer_name,notes))
        if product_id:
            c.execute("UPDATE products SET quantity=quantity-? WHERE id=?",(quantity,product_id))
        milestone=_check_milestones(c,user_id)
        return cur.lastrowid, milestone

def _check_milestones(c, user_id=None):
    count=c.execute("SELECT COUNT(*) FROM sales WHERE DATE(sale_date)=DATE('now')").fetchone()[0]
    for m in [1,5,10,25,50,100]:
        if count==m:
            if not c.execute("""SELECT id FROM gamification WHERE milestone_type='daily_sales'
                AND milestone_value=? AND DATE(achieved_at)=DATE('now')""",(m,)).fetchone():
                c.execute("INSERT INTO gamification(milestone_type,milestone_value,user_id) VALUES('daily_sales',?,?)",(m,user_id))
                return m
    return None

def get_sales_summary(days=30):
    with get_connection() as c:
        r=c.execute("""SELECT COUNT(*) total_sales,COALESCE(SUM(total_price),0) total_revenue,
            COALESCE(SUM(profit),0) total_profit,COALESCE(SUM(tax_amount),0) total_tax,
            COALESCE(AVG(total_price),0) avg_ticket FROM sales WHERE sale_date>=datetime('now',?)""",
            (f"-{days} days",)).fetchone()
        return dict(r)

def get_sales_by_day(days=30):
    with get_connection() as c:
        return [dict(r) for r in c.execute("""SELECT DATE(sale_date) day,COUNT(*) count,
            SUM(total_price) revenue,SUM(profit) profit FROM sales
            WHERE sale_date>=datetime('now',?) GROUP BY DATE(sale_date) ORDER BY day""",
            (f"-{days} days",)).fetchall()]

def get_top_products(limit=10, days=30):
    with get_connection() as c:
        return [dict(r) for r in c.execute("""SELECT product_name,SUM(quantity) total_qty,
            SUM(total_price) total_revenue,SUM(profit) total_profit FROM sales
            WHERE sale_date>=datetime('now',?) GROUP BY product_name ORDER BY total_revenue DESC LIMIT ?""",
            (f"-{days} days",limit)).fetchall()]

def get_financial_summary(days=30):
    with get_connection() as c:
        s=c.execute("""SELECT COALESCE(SUM(total_price),0) revenue,COALESCE(SUM(profit),0) gross_profit,
            COALESCE(SUM(tax_amount),0) taxes,COUNT(*) total_sales FROM sales
            WHERE sale_date>=datetime('now',?)""",(f"-{days} days",)).fetchone()
        e=c.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE expense_date>=datetime('now',?)",
            (f"-{days} days",)).fetchone()
        rev,gp,tx,cnt,exp=s[0],s[1],s[2],s[3],e[0]; net=gp-exp
        return {"revenue":rev,"gross_profit":gp,"taxes":tx,"expenses":exp,
                "net_profit":net,"total_sales":cnt,"margin_pct":(net/rev*100) if rev>0 else 0}

def add_expense(description, amount, category="outros", payment_method="", notes=""):
    with get_connection() as c:
        cur=c.execute("INSERT INTO expenses(description,amount,category,payment_method,notes) VALUES(?,?,?,?,?)",
                      (description,amount,category,payment_method,notes))
        return cur.lastrowid

def get_recent_milestones(minutes=5):
    with get_connection() as c:
        return [dict(r) for r in c.execute("""SELECT * FROM gamification
            WHERE achieved_at>=datetime('now',?) ORDER BY achieved_at DESC""",
            (f"-{minutes} minutes",)).fetchall()]
