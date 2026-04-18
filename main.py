"""
ErosGest AI — Gestão Inteligente para Revendedores
Interface principal com tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import sys
import logging
import webbrowser
from datetime import datetime
from pathlib import Path

# Setup de paths
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Logging
log_dir = Path.home() / ".erosgest" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "erosgest.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ErosGest")

# ─── TEMA E CORES ────────────────────────────────────────────────────────────
THEMES = {
    "dark": {"name":"🌙 Escuro (Padrão)",
        "bg_dark":"#0D0D1A","bg_card":"#141428","bg_hover":"#1C1C35",
        "accent":"#7C3AED","accent_light":"#A855F7","accent_dim":"#4C1D95",
        "green":"#10B981","green_dim":"#064E3B","red":"#EF4444","red_dim":"#7F1D1D",
        "yellow":"#F59E0B","yellow_dim":"#78350F","blue":"#3B82F6",
        "text_bright":"#F5F3FF","text_main":"#C4B5FD","text_muted":"#7C6FAC",
        "border":"#2D2B4E","input_bg":"#1A1A2E"},
    "light": {"name":"☀️ Claro",
        "bg_dark":"#F0EFFA","bg_card":"#FFFFFF","bg_hover":"#E8E5F8",
        "accent":"#7C3AED","accent_light":"#6D28D9","accent_dim":"#DDD6FE",
        "green":"#059669","green_dim":"#D1FAE5","red":"#DC2626","red_dim":"#FEE2E2",
        "yellow":"#D97706","yellow_dim":"#FEF3C7","blue":"#2563EB",
        "text_bright":"#1E1B4B","text_main":"#4C1D95","text_muted":"#6B7280",
        "border":"#E5E7EB","input_bg":"#F3F4F6"},
    "neon": {"name":"⚡ Neon",
        "bg_dark":"#050510","bg_card":"#0A0A20","bg_hover":"#0F0F2A",
        "accent":"#00FF88","accent_light":"#00DDFF","accent_dim":"#003322",
        "green":"#00FF88","green_dim":"#002211","red":"#FF3366","red_dim":"#330011",
        "yellow":"#FFD700","yellow_dim":"#332200","blue":"#00DDFF",
        "text_bright":"#E0FFF8","text_main":"#00FF88","text_muted":"#4488AA",
        "border":"#003344","input_bg":"#080818"},
    "red": {"name":"🔴 Vermelho",
        "bg_dark":"#0F0505","bg_card":"#1A0808","bg_hover":"#220A0A",
        "accent":"#DC2626","accent_light":"#EF4444","accent_dim":"#7F1D1D",
        "green":"#16A34A","green_dim":"#14532D","red":"#F87171","red_dim":"#450A0A",
        "yellow":"#F59E0B","yellow_dim":"#78350F","blue":"#3B82F6",
        "text_bright":"#FFF5F5","text_main":"#FCA5A5","text_muted":"#9CA3AF",
        "border":"#450A0A","input_bg":"#150606"},
}

COLORS = THEMES["dark"].copy()  # tema ativo

def apply_theme(name):
    global COLORS
    t = THEMES.get(name, THEMES["dark"])
    COLORS.clear()
    COLORS.update(t)

FONTS = {
    "title":   ("Segoe UI", 22, "bold"),
    "heading": ("Segoe UI", 14, "bold"),
    "sub":     ("Segoe UI", 11, "bold"),
    "body":    ("Segoe UI", 10),
    "small":   ("Segoe UI", 9),
    "mono":    ("Consolas", 10),
    "big_num": ("Segoe UI", 28, "bold"),
    "nav":     ("Segoe UI", 11, "bold"),
}


def setup_style():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure(".", background=COLORS["bg_dark"], foreground=COLORS["text_main"],
                    fieldbackground=COLORS["input_bg"], borderwidth=0, relief="flat")
    style.configure("TFrame", background=COLORS["bg_dark"])
    style.configure("Card.TFrame", background=COLORS["bg_card"])
    style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_main"])
    style.configure("Card.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_main"])
    style.configure("Title.TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_bright"],
                    font=FONTS["title"])
    style.configure("Heading.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_bright"],
                    font=FONTS["heading"])
    style.configure("BigNum.TLabel", background=COLORS["bg_card"], foreground=COLORS["accent_light"],
                    font=FONTS["big_num"])
    style.configure("Green.TLabel", background=COLORS["bg_card"], foreground=COLORS["green"])
    style.configure("Red.TLabel", background=COLORS["bg_card"], foreground=COLORS["red"])
    style.configure("Muted.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_muted"],
                    font=FONTS["small"])

    style.configure("Accent.TButton", background=COLORS["accent"], foreground=COLORS["text_bright"],
                    font=FONTS["sub"], borderwidth=0, relief="flat", padding=(16, 10))
    style.map("Accent.TButton",
              background=[("active", COLORS["accent_light"]), ("pressed", COLORS["accent_dim"])],
              foreground=[("active", "#FFFFFF")])

    style.configure("Ghost.TButton", background=COLORS["bg_card"], foreground=COLORS["text_main"],
                    font=FONTS["body"], borderwidth=1, relief="solid", padding=(12, 8))
    style.map("Ghost.TButton",
              background=[("active", COLORS["bg_hover"])],
              foreground=[("active", COLORS["text_bright"])])

    style.configure("Green.TButton", background=COLORS["green_dim"], foreground=COLORS["green"],
                    font=FONTS["sub"], borderwidth=0, padding=(12, 8))
    style.map("Green.TButton", background=[("active", COLORS["green"])])

    style.configure("Treeview", background=COLORS["bg_card"], foreground=COLORS["text_main"],
                    fieldbackground=COLORS["bg_card"], borderwidth=0, rowheight=28,
                    font=FONTS["body"])
    style.configure("Treeview.Heading", background=COLORS["bg_dark"], foreground=COLORS["text_muted"],
                    font=FONTS["small"], borderwidth=0)
    style.map("Treeview", background=[("selected", COLORS["accent_dim"])],
              foreground=[("selected", COLORS["text_bright"])])

    style.configure("TEntry", fieldbackground=COLORS["input_bg"], foreground=COLORS["text_bright"],
                    insertcolor=COLORS["accent_light"], borderwidth=1, relief="solid",
                    padding=(8, 6))
    style.configure("TCombobox", fieldbackground=COLORS["input_bg"], foreground=COLORS["text_bright"],
                    background=COLORS["input_bg"], arrowcolor=COLORS["accent_light"])
    style.configure("TScrollbar", background=COLORS["bg_dark"], troughcolor=COLORS["bg_card"],
                    arrowcolor=COLORS["text_muted"])
    style.configure("TNotebook", background=COLORS["bg_dark"], borderwidth=0)
    style.configure("TNotebook.Tab", background=COLORS["bg_card"], foreground=COLORS["text_muted"],
                    font=FONTS["body"], padding=(16, 8))
    style.map("TNotebook.Tab",
              background=[("selected", COLORS["bg_dark"])],
              foreground=[("selected", COLORS["accent_light"])])
    style.configure("Horizontal.TProgressbar",
                    troughcolor=COLORS["bg_dark"], background=COLORS["accent"],
                    borderwidth=0, thickness=6)


# ─── WIDGETS CUSTOMIZADOS ─────────────────────────────────────────────────────

class MetricCard(tk.Frame):
    def __init__(self, parent, title, value, subtitle="", color=None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], padx=20, pady=16, **kwargs)
        self.configure(highlightbackground=COLORS["border"], highlightthickness=1)

        self._color = color or COLORS["accent_light"]
        self._val_var = tk.StringVar(value=value)
        self._sub_var = tk.StringVar(value=subtitle)

        tk.Label(self, text=title, font=FONTS["small"], bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"]).pack(anchor="w")
        tk.Label(self, textvariable=self._val_var, font=FONTS["big_num"],
                 bg=COLORS["bg_card"], fg=self._color).pack(anchor="w", pady=(4, 0))
        tk.Label(self, textvariable=self._sub_var, font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w")

    def update_value(self, value, subtitle=None):
        self._val_var.set(value)
        if subtitle is not None:
            self._sub_var.set(subtitle)


class SectionHeader(tk.Frame):
    def __init__(self, parent, title, subtitle="", **kwargs):
        super().__init__(parent, bg=COLORS["bg_dark"], **kwargs)
        tk.Label(self, text=title, font=FONTS["heading"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_bright"]).pack(side="left")
        if subtitle:
            tk.Label(self, text=f"  {subtitle}", font=FONTS["small"],
                     bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side="left", pady=(4, 0))


class StyledEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        kwargs.setdefault("bg", COLORS["input_bg"])
        kwargs.setdefault("fg", COLORS["text_bright"])
        kwargs.setdefault("insertbackground", COLORS["accent_light"])
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("font", FONTS["body"])
        kwargs.setdefault("bd", 0)
        super().__init__(parent, **kwargs)
        self._placeholder = placeholder
        self._has_placeholder = False
        if placeholder:
            self._show_placeholder()
            self.bind("<FocusIn>", self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self):
        self.insert(0, self._placeholder)
        self.config(fg=COLORS["text_muted"])
        self._has_placeholder = True

    def _on_focus_in(self, e):
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.config(fg=COLORS["text_bright"])
            self._has_placeholder = False

    def _on_focus_out(self, e):
        if not self.get():
            self._show_placeholder()

    def get_value(self):
        if self._has_placeholder:
            return ""
        return self.get()


# ─── TELAS ───────────────────────────────────────────────────────────────────

class DashboardTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_dark"])
        header.pack(fill="x", padx=24, pady=(20, 16))
        tk.Label(header, text="📊 Dashboard", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(side="left")
        ttk.Button(header, text="↻ Atualizar", style="Ghost.TButton",
                   command=self.refresh).pack(side="right")

        # Cards de métricas
        cards_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        cards_frame.pack(fill="x", padx=24, pady=(0, 16))

        self.card_revenue = MetricCard(cards_frame, "RECEITA (30 DIAS)", "R$ 0,00",
                                        color=COLORS["green"])
        self.card_revenue.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.card_profit = MetricCard(cards_frame, "LUCRO LÍQUIDO", "R$ 0,00",
                                       color=COLORS["accent_light"])
        self.card_profit.pack(side="left", fill="both", expand=True, padx=8)

        self.card_sales = MetricCard(cards_frame, "VENDAS REALIZADAS", "0",
                                      color=COLORS["yellow"])
        self.card_sales.pack(side="left", fill="both", expand=True, padx=8)

        self.card_margin = MetricCard(cards_frame, "MARGEM LÍQUIDA", "0%",
                                       color=COLORS["blue"])
        self.card_margin.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # Gráfico simples de vendas diárias (canvas)
        chart_card = tk.Frame(self, bg=COLORS["bg_card"],
                               highlightbackground=COLORS["border"], highlightthickness=1)
        chart_card.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        tk.Label(chart_card, text="Vendas Diárias — Últimos 30 Dias",
                 font=FONTS["sub"], bg=COLORS["bg_card"], fg=COLORS["text_bright"]).pack(
            anchor="w", padx=16, pady=(12, 0))

        self.canvas = tk.Canvas(chart_card, bg=COLORS["bg_card"], height=180,
                                 highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        # Alertas de estoque
        alert_card = tk.Frame(self, bg=COLORS["bg_card"],
                               highlightbackground=COLORS["border"], highlightthickness=1)
        alert_card.pack(fill="x", padx=24, pady=(0, 16))
        tk.Label(alert_card, text="⚠️ Alertas de Estoque Baixo",
                 font=FONTS["sub"], bg=COLORS["bg_card"], fg=COLORS["yellow"]).pack(
            anchor="w", padx=16, pady=(12, 4))

        self.alerts_frame = tk.Frame(alert_card, bg=COLORS["bg_card"])
        self.alerts_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.refresh()

    def refresh(self):
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            from database.db import get_financial_summary, get_sales_by_day, get_products, get_sales_summary

            fin = get_financial_summary(30)
            sales_sum = get_sales_summary(30)
            daily = get_sales_by_day(30)
            low_stock = get_products(active_only=True, low_stock=True)

            self.after(0, lambda: self._update_ui(fin, sales_sum, daily, low_stock))
        except Exception as e:
            logger.error(f"Dashboard load error: {e}")

    def _update_ui(self, fin, sales_sum, daily, low_stock):
        r = fin.get("revenue", 0)
        p = fin.get("net_profit", 0)
        t = fin.get("taxes", 0)
        m = fin.get("margin_pct", 0)
        cnt = sales_sum.get("total_sales", 0)

        self.card_revenue.update_value(f"R$ {r:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                        f"Impostos: R$ {t:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.card_profit.update_value(f"R$ {p:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                                       "após despesas e impostos")
        self.card_sales.update_value(str(cnt), f"ticket médio: R$ {sales_sum.get('avg_ticket', 0):.2f}")
        self.card_margin.update_value(f"{m:.1f}%",
                                       "saudável > 20%" if m >= 20 else "atenção: margem baixa")

        self._draw_chart(daily)

        # Alertas
        for w in self.alerts_frame.winfo_children():
            w.destroy()

        if not low_stock:
            tk.Label(self.alerts_frame, text="✅ Todos os produtos com estoque adequado",
                     font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["green"]).pack(anchor="w")
        else:
            for p in low_stock[:5]:
                row = tk.Frame(self.alerts_frame, bg=COLORS["bg_card"])
                row.pack(fill="x", pady=2)
                tk.Label(row, text=f"⚠️ {p['name']}", font=FONTS["body"],
                         bg=COLORS["bg_card"], fg=COLORS["yellow"]).pack(side="left")
                tk.Label(row, text=f" — {p['quantity']} {p['unit']} restante(s)",
                         font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left")

    def _draw_chart(self, daily_data):
        self.canvas.delete("all")
        if not daily_data:
            self.canvas.create_text(self.canvas.winfo_width() // 2 or 300, 90,
                                     text="Sem dados de vendas ainda", fill=COLORS["text_muted"],
                                     font=FONTS["body"])
            return

        self.canvas.update_idletasks()
        W = self.canvas.winfo_width() or 600
        H = self.canvas.winfo_height() or 180
        pad_l, pad_r, pad_t, pad_b = 40, 20, 20, 30

        revenues = [d["revenue"] for d in daily_data]
        max_val = max(revenues) if revenues else 1
        if max_val == 0:
            max_val = 1

        # Linhas de grade
        for i in range(4):
            y = pad_t + (H - pad_t - pad_b) * i / 3
            self.canvas.create_line(pad_l, y, W - pad_r, y,
                                     fill=COLORS["border"], dash=(4, 4))
            val = max_val * (1 - i / 3)
            self.canvas.create_text(pad_l - 4, y, text=f"R${val:.0f}",
                                     anchor="e", fill=COLORS["text_muted"],
                                     font=("Segoe UI", 8))

        n = len(daily_data)
        if n < 2:
            return

        bar_w = max(4, (W - pad_l - pad_r) / n - 3)
        points = []
        for i, d in enumerate(daily_data):
            x = pad_l + (W - pad_l - pad_r) * i / (n - 1)
            y_h = (H - pad_t - pad_b) * (d["revenue"] / max_val)
            y = H - pad_b - y_h
            points.append((x, y))

            # Barras
            self.canvas.create_rectangle(
                x - bar_w/2, H - pad_b, x + bar_w/2, y,
                fill=COLORS["accent_dim"], outline="", width=0
            )

        # Linha de tendência
        if len(points) >= 2:
            flat = [coord for pt in points for coord in pt]
            self.canvas.create_line(*flat, fill=COLORS["accent_light"],
                                     width=2, smooth=True, joinstyle="round")

        # Pontos
        for x, y in points:
            self.canvas.create_oval(x-3, y-3, x+3, y+3,
                                     fill=COLORS["accent_light"], outline=COLORS["bg_card"], width=1)


class ProductsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_dark"])
        header.pack(fill="x", padx=24, pady=(20, 16))
        tk.Label(header, text="📦 Estoque", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(side="left")

        btn_frame = tk.Frame(header, bg=COLORS["bg_dark"])
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="+ Novo Produto", style="Accent.TButton",
                   command=self._add_dialog).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="↻ Atualizar", style="Ghost.TButton",
                   command=self.refresh).pack(side="left", padx=4)

        # Filtros
        filter_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        filter_frame.pack(fill="x", padx=24, pady=(0, 12))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var,
                                bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                                font=FONTS["body"], relief="flat", bd=0,
                                insertbackground=COLORS["accent_light"])
        search_entry.pack(side="left", fill="x", expand=True, ipady=8, ipadx=10)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        self.cat_var = tk.StringVar(value="Todas")
        cat_combo = ttk.Combobox(filter_frame, textvariable=self.cat_var,
                                  values=["Todas", "eletrônicos", "alimentos", "roupas",
                                           "cosméticos", "outros"],
                                  width=15, state="readonly")
        cat_combo.pack(side="left", padx=(8, 0))
        cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Tabela de produtos
        table_frame = tk.Frame(self, bg=COLORS["bg_card"],
                                highlightbackground=COLORS["border"], highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        cols = ("name", "category", "quantity", "cost", "price", "margin", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=20)

        headers = {"name": ("Produto", 200), "category": ("Categoria", 100),
                   "quantity": ("Qtd", 60), "cost": ("Custo", 90),
                   "price": ("Preço Venda", 100), "margin": ("Margem", 80),
                   "status": ("Status", 90)}

        for col, (label, width) in headers.items():
            self.tree.heading(col, text=label, anchor="w")
            self.tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.tag_configure("low_stock", foreground=COLORS["yellow"])
        self.tree.tag_configure("normal", foreground=COLORS["text_main"])
        self.tree.tag_configure("no_stock", foreground=COLORS["red"])

        self.refresh()

    def refresh(self):
        threading.Thread(target=self._load_products, daemon=True).start()

    def _load_products(self):
        try:
            from database.db import get_products
            search = self.search_var.get().lower()
            cat = self.cat_var.get()
            products = get_products(active_only=True, category=None if cat == "Todas" else cat)
            if search:
                products = [p for p in products if search in p["name"].lower()]
            self.after(0, lambda: self._populate_table(products))
        except Exception as e:
            logger.error(f"Products load: {e}")

    def _populate_table(self, products):
        self.tree.delete(*self.tree.get_children())
        self._products_data = products

        for p in products:
            margin = 0
            if p["sale_price"] > 0:
                margin = (p["sale_price"] - p["cost_price"]) / p["sale_price"] * 100

            if p["quantity"] <= 0:
                tag = "no_stock"
                status = "🔴 Sem estoque"
            elif p["quantity"] <= p.get("min_quantity", 5):
                tag = "low_stock"
                status = "⚠️ Baixo"
            else:
                tag = "normal"
                status = "✅ OK"

            self.tree.insert("", tk.END, iid=str(p["id"]), tags=(tag,), values=(
                p["name"],
                p["category"] or "-",
                f"{p['quantity']} {p['unit']}",
                f"R$ {p['cost_price']:.2f}",
                f"R$ {p['sale_price']:.2f}",
                f"{margin:.1f}%",
                status
            ))

    def _add_dialog(self):
        ProductDialog(self.app, on_save=self.refresh)

    def _on_double_click(self, event):
        item = self.tree.focus()
        if not item:
            return
        product_id = int(item)
        products = getattr(self, '_products_data', [])
        product = next((p for p in products if p["id"] == product_id), None)
        if product:
            ProductDialog(self.app, product=product, on_save=self.refresh)


class ProductDialog(tk.Toplevel):
    def __init__(self, parent, product=None, on_save=None):
        super().__init__(parent)
        self.product = product
        self.on_save = on_save
        self.title("Editar Produto" if product else "Novo Produto")
        self.configure(bg=COLORS["bg_dark"])
        self.geometry("550x620")
        self.resizable(False, False)
        self.grab_set()
        self.image_path = None
        self._build()

    def _build(self):
        tk.Label(self, text="Produto" if not self.product else self.product["name"],
                 font=FONTS["heading"], bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(
            padx=24, pady=(20, 16), anchor="w")

        form = tk.Frame(self, bg=COLORS["bg_dark"])
        form.pack(fill="both", expand=True, padx=24)

        def field(label, row, default="", col=0):
            tk.Label(form, text=label, font=FONTS["small"], bg=COLORS["bg_dark"],
                     fg=COLORS["text_muted"]).grid(row=row*2, column=col, sticky="w", pady=(8, 2))
            entry = tk.Entry(form, bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                              font=FONTS["body"], relief="flat", bd=0,
                              insertbackground=COLORS["accent_light"])
            entry.grid(row=row*2+1, column=col, sticky="ew", ipady=8, ipadx=8,
                       padx=(0, 8) if col == 0 else (8, 0))
            if default:
                entry.insert(0, str(default))
            return entry

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        p = self.product or {}
        self.e_name = field("Nome do Produto *", 0, p.get("name", ""), col=0)
        self.e_ean = field("EAN / Código", 0, p.get("ean", ""), col=1)
        self.e_qty = field("Quantidade *", 1, p.get("quantity", ""), col=0)
        self.e_unit = field("Unidade (un/kg/cx)", 1, p.get("unit", "un"), col=1)
        self.e_cost = field("Preço de Custo (R$) *", 2, p.get("cost_price", ""), col=0)
        self.e_price = field("Preço de Venda (R$)", 2, p.get("sale_price", ""), col=1)
        self.e_min_qty = field("Estoque Mínimo", 3, p.get("min_quantity", "5"), col=0)

        tk.Label(form, text="Categoria", font=FONTS["small"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).grid(row=7, column=1, sticky="w", pady=(8, 2), padx=(8, 0))
        self.cat_var = tk.StringVar(value=p.get("category", "outros"))
        cat_combo = ttk.Combobox(form, textvariable=self.cat_var,
                                  values=["eletrônicos", "alimentos", "roupas", "cosméticos", "outros"],
                                  width=18)
        cat_combo.grid(row=8, column=1, sticky="ew", padx=(8, 0), ipady=6)

        self.e_supplier = field("Fornecedor", 4, p.get("supplier", ""), col=0)

        tk.Label(form, text="Observações", font=FONTS["small"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).grid(row=9, column=0, columnspan=2, sticky="w", pady=(8, 2))
        self.e_notes = tk.Text(form, bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                                font=FONTS["body"], height=2, relief="flat", bd=0)
        self.e_notes.grid(row=10, column=0, columnspan=2, sticky="ew", ipady=4, ipadx=8)
        if p.get("notes"):
            self.e_notes.insert("1.0", p["notes"])

        # Seção de imagem
        img_frame = tk.Frame(form, bg=COLORS["bg_dark"])
        img_frame.grid(row=11, column=0, columnspan=2, pady=(12, 0), sticky="ew")
        
        tk.Label(img_frame, text="Foto do Produto", font=FONTS["small"], bg=COLORS["bg_dark"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(8, 4))
        
        btn_img_frame = tk.Frame(img_frame, bg=COLORS["bg_dark"])
        btn_img_frame.pack(fill="x")
        
        ttk.Button(btn_img_frame, text="📷 Selecionar Foto", style="Ghost.TButton",
                   command=self._select_image).pack(side="left")
        
        self.lbl_image_status = tk.Label(btn_img_frame, text="", font=FONTS["small"],
                                          bg=COLORS["bg_dark"], fg=COLORS["text_muted"])
        self.lbl_image_status.pack(side="left", padx=(10, 0))
        
        # Preview da imagem (se existir)
        self.lbl_preview = tk.Label(img_frame, bg=COLORS["bg_dark"], fg=COLORS["text_muted"],
                                     font=FONTS["small"])
        self.lbl_preview.pack(anchor="w", pady=(4, 0))
        
        if p.get("image_url"):
            self.lbl_image_status.config(text="✓ Imagem salva")
            self.lbl_preview.config(text="Imagem já cadastrada")

        # Botões
        btn_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        btn_frame.pack(fill="x", padx=24, pady=20)

        if self.product:
            ttk.Button(btn_frame, text="🗑 Excluir", style="Ghost.TButton",
                       command=self._delete).pack(side="left")

        ttk.Button(btn_frame, text="Cancelar", style="Ghost.TButton",
                   command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btn_frame, text="💾 Salvar", style="Accent.TButton",
                   command=self._save).pack(side="right")

    def _select_image(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Selecionar foto do produto",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.image_path = file_path
            filename = file_path.split("/")[-1]
            self.lbl_image_status.config(text=f"✓ {filename}")
            self.lbl_preview.config(text="Foto selecionada - será salva com o produto")

    def _save(self):
        name = self.e_name.get().strip()
        if not name:
            messagebox.showerror("Erro", "Nome do produto é obrigatório", parent=self)
            return

        try:
            qty = int(self.e_qty.get().strip() or 0)
            cost = float(self.e_cost.get().strip().replace(",", ".") or 0)
            price = float(self.e_price.get().strip().replace(",", ".") or 0)
            min_qty = int(self.e_min_qty.get().strip() or 5)
        except ValueError as e:
            messagebox.showerror("Erro", f"Valores numéricos inválidos: {e}", parent=self)
            return

        if cost <= 0:
            messagebox.showerror("Erro", "Preço de custo deve ser maior que zero", parent=self)
            return

        if price == 0:
            # Sugere margem padrão de 30%
            price = round(cost * 1.35, 2)

        notes = self.e_notes.get("1.0", tk.END).strip()
        
        # Carregar imagem se selecionada
        image_data = None
        if self.image_path:
            try:
                with open(self.image_path, "rb") as f:
                    image_data = f.read()
            except Exception as e:
                messagebox.showwarning("Aviso", f"Não foi possível carregar a imagem: {e}")

        try:
            from database.db import add_product, update_product
            if self.product:
                update_kwargs = {
                    "name": name, "quantity": qty, "cost_price": cost, "sale_price": price,
                    "category": self.cat_var.get(), "supplier": self.e_supplier.get().strip(),
                    "ean": self.e_ean.get().strip(), "unit": self.e_unit.get().strip() or "un",
                    "notes": notes, "min_quantity": min_qty
                }
                # Se nova imagem foi selecionada, atualiza também
                if image_data:
                    from database.db import get_connection
                    import base64
                    image_url = "data:image/png;base64," + base64.b64encode(image_data).decode('utf-8')
                    update_kwargs["image_url"] = image_url
                update_product(self.product["id"], **update_kwargs)
            else:
                add_product(name=name, cost_price=cost, sale_price=price,
                            quantity=qty, category=self.cat_var.get(),
                            supplier=self.e_supplier.get().strip(),
                            ean=self.e_ean.get().strip(),
                            unit=self.e_unit.get().strip() or "un",
                            notes=notes, image_data=image_data)

            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e), parent=self)

    def _delete(self):
        if messagebox.askyesno("Confirmar", f"Excluir '{self.product['name']}'?", parent=self):
            try:
                from database.db import update_product
                update_product(self.product["id"], active=0)
                if self.on_save:
                    self.on_save()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e), parent=self)


class SalesTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg_dark"])
        header.pack(fill="x", padx=24, pady=(20, 16))
        tk.Label(header, text="💰 Vendas", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(side="left")
        ttk.Button(header, text="+ Nova Venda", style="Accent.TButton",
                   command=self._new_sale_dialog).pack(side="right")

        # Painel de nova venda rápida
        quick = tk.Frame(self, bg=COLORS["bg_card"],
                          highlightbackground=COLORS["border"], highlightthickness=1)
        quick.pack(fill="x", padx=24, pady=(0, 16))

        tk.Label(quick, text="Venda Rápida", font=FONTS["sub"],
                 bg=COLORS["bg_card"], fg=COLORS["text_bright"]).pack(padx=16, pady=(12, 8), anchor="w")

        row = tk.Frame(quick, bg=COLORS["bg_card"])
        row.pack(fill="x", padx=16, pady=(0, 12))

        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(row, textvariable=self.product_var, width=30)
        self.product_combo.pack(side="left")
        self.product_combo.bind("<<ComboboxSelected>>", self._on_product_selected)

        tk.Label(row, text="  Qtd:", font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left")
        self.qty_var = tk.StringVar(value="1")
        tk.Entry(row, textvariable=self.qty_var, width=6,
                 bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                 font=FONTS["body"], relief="flat", bd=0,
                 insertbackground=COLORS["accent_light"]).pack(side="left", ipady=6, ipadx=4)

        tk.Label(row, text="  Preço R$:", font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left")
        self.price_var = tk.StringVar()
        tk.Entry(row, textvariable=self.price_var, width=10,
                 bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                 font=FONTS["body"], relief="flat", bd=0,
                 insertbackground=COLORS["accent_light"]).pack(side="left", ipady=6, ipadx=4)

        self.payment_var = tk.StringVar(value="dinheiro")
        pay_combo = ttk.Combobox(row, textvariable=self.payment_var, width=12,
                                  values=["dinheiro", "pix", "cartão débito", "cartão crédito", "fiado"],
                                  state="readonly")
        pay_combo.pack(side="left", padx=8)

        ttk.Button(row, text="✓ Registrar", style="Green.TButton",
                   command=self._quick_sale).pack(side="left", padx=4)

        # Histórico de vendas
        tk.Label(self, text="Histórico de Vendas", font=FONTS["sub"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(padx=24, anchor="w")

        table_frame = tk.Frame(self, bg=COLORS["bg_card"],
                                highlightbackground=COLORS["border"], highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(8, 16))

        cols = ("date", "product", "qty", "price", "total", "profit", "payment")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        headers = {"date": ("Data/Hora", 130), "product": ("Produto", 180),
                   "qty": ("Qtd", 50), "price": ("Preço Un.", 90),
                   "total": ("Total", 90), "profit": ("Lucro", 80),
                   "payment": ("Pagamento", 120)}

        for col, (label, width) in headers.items():
            self.tree.heading(col, text=label, anchor="w")
            self.tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("profit_ok", foreground=COLORS["text_main"])
        self.tree.tag_configure("profit_low", foreground=COLORS["yellow"])

        self.refresh()

    def refresh(self):
        # Carrega produtos para o combo
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            from database.db import get_products, get_connection
            products = get_products(active_only=True)
            self._products = {p["name"]: p for p in products}

            with get_connection() as conn:
                rows = conn.execute("""
                    SELECT sale_date, product_name, quantity, unit_price,
                           total_price, profit, payment_method
                    FROM sales ORDER BY sale_date DESC LIMIT 100
                """).fetchall()
                sales = [dict(r) for r in rows]

            self.after(0, lambda: self._update_ui(products, sales))
        except Exception as e:
            logger.error(f"Sales load: {e}")

    def _update_ui(self, products, sales):
        self.product_combo["values"] = [p["name"] for p in products]

        self.tree.delete(*self.tree.get_children())
        for s in sales:
            tag = "profit_ok" if s["profit"] >= 0 else "profit_low"
            dt = s["sale_date"][:16] if s["sale_date"] else ""
            self.tree.insert("", tk.END, tags=(tag,), values=(
                dt,
                s["product_name"],
                s["quantity"],
                f"R$ {s['unit_price']:.2f}",
                f"R$ {s['total_price']:.2f}",
                f"R$ {s['profit']:.2f}",
                s["payment_method"]
            ))

    def _on_product_selected(self, event):
        name = self.product_var.get()
        if name in getattr(self, '_products', {}):
            p = self._products[name]
            self.price_var.set(f"{p['sale_price']:.2f}")

    def _quick_sale(self):
        name = self.product_var.get().strip()
        if not name:
            messagebox.showerror("Erro", "Selecione um produto")
            return

        try:
            qty = int(self.qty_var.get())
            price = float(self.price_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preço devem ser números válidos")
            return

        products = getattr(self, "_products", {})
        if name not in products:
            messagebox.showerror("Erro", f"Produto '{name}' não encontrado")
            return

        p = products[name]
        total = qty * price
        profit = (price - p["cost_price"]) * qty

        confirm = messagebox.askyesno(
            "Confirmar Venda",
            f"Produto: {name}\nQuantidade: {qty}\nTotal: R$ {total:.2f}\nLucro: R$ {profit:.2f}\n\nConfirmar?"
        )
        if not confirm:
            return

        try:
            from database.db import record_sale
            sale_id, milestone = record_sale(p["id"], name, qty, price, p["cost_price"],
                        payment_method=self.payment_var.get())
            messagebox.showinfo("✅ Venda Registrada", f"Venda de {qty}x {name} registrada!\nTotal: R$ {total:.2f}")
            self.refresh()
            if milestone:
                self.app._show_achievement(milestone)
            else:
                self.app.check_gamification()
        except Exception as e:
            messagebox.showerror("Erro na Venda", str(e))

    def _new_sale_dialog(self):
        self._quick_sale()


class AssistantTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._history = []
        self._voice = None
        self._build()

    def _build(self):
        tk.Label(self, text="🤖 Assistente IA", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(padx=24, pady=(20, 4), anchor="w")
        tk.Label(self, text="Chat inteligente com contexto real do seu estoque e finanças",
                 font=FONTS["small"], bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(padx=24, anchor="w")

        # Config API
        api_bar = tk.Frame(self, bg=COLORS["bg_card"],
                            highlightbackground=COLORS["border"], highlightthickness=1)
        api_bar.pack(fill="x", padx=24, pady=(12, 0))
        tk.Label(api_bar, text="OpenAI API Key:", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left", padx=(12, 4))
        self.api_entry = tk.Entry(api_bar, show="*", width=40,
                                   bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                                   font=FONTS["mono"], relief="flat", bd=0,
                                   insertbackground=COLORS["accent_light"])
        self.api_entry.pack(side="left", ipady=6, ipadx=8)
        from database.db import get_config
        saved_key = get_config("openai_api_key", "")
        if saved_key:
            self.api_entry.insert(0, saved_key)
        ttk.Button(api_bar, text="Salvar", style="Ghost.TButton",
                   command=self._save_api_key).pack(side="left", padx=8)
        tk.Label(api_bar, text="Sem chave? ", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="right", padx=(0, 4))
        link = tk.Label(api_bar, text="platform.openai.com", font=FONTS["small"],
                         bg=COLORS["bg_card"], fg=COLORS["blue"], cursor="hand2")
        link.pack(side="right", padx=(0, 12))
        link.bind("<Button-1>", lambda e: webbrowser.open("https://platform.openai.com/api-keys"))

        # Chat area
        chat_frame = tk.Frame(self, bg=COLORS["bg_card"],
                               highlightbackground=COLORS["border"], highlightthickness=1)
        chat_frame.pack(fill="both", expand=True, padx=24, pady=12)

        self.chat_text = tk.Text(chat_frame, bg=COLORS["bg_card"], fg=COLORS["text_main"],
                                  font=FONTS["body"], relief="flat", state="disabled",
                                  wrap="word", padx=16, pady=12, cursor="arrow")
        scroll = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=scroll.set)
        self.chat_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Tags de formatação do chat
        self.chat_text.tag_configure("user", foreground=COLORS["accent_light"], font=("Segoe UI", 10, "bold"))
        self.chat_text.tag_configure("assistant", foreground=COLORS["text_bright"], font=FONTS["body"])
        self.chat_text.tag_configure("system", foreground=COLORS["text_muted"], font=FONTS["small"])
        self.chat_text.tag_configure("error", foreground=COLORS["red"], font=FONTS["body"])
        self.chat_text.tag_configure("action", foreground=COLORS["green"], font=FONTS["body"])

        # Input
        input_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        input_frame.pack(fill="x", padx=24, pady=(0, 16))

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(input_frame, textvariable=self.input_var,
                                     bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                                     font=FONTS["body"], relief="flat", bd=0,
                                     insertbackground=COLORS["accent_light"])
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=10, ipadx=12)
        self.input_entry.bind("<Return>", lambda e: self._send_message())

        self._tts_enabled = True
        self._voice_active = False
        self.voice_btn = ttk.Button(input_frame, text="🎤", style="Ghost.TButton",
                                     command=self._start_voice)
        self.voice_btn.pack(side="left", padx=4)

        self.tts_var = tk.BooleanVar(value=True)
        def toggle_tts():
            self._tts_enabled = self.tts_var.get()
        tk.Checkbutton(input_frame, text="🔊 Voz", variable=self.tts_var,
                        bg=COLORS["bg_dark"], fg=COLORS["text_main"],
                        selectcolor=COLORS["accent_dim"], activebackground=COLORS["bg_dark"],
                        font=FONTS["small"], cursor="hand2",
                        command=toggle_tts).pack(side="left", padx=(0,6))

        ttk.Button(input_frame, text="Enviar →", style="Accent.TButton",
                   command=self._send_message).pack(side="left")

        # Mensagem de boas-vindas
        self._append_message("sistema",
                              "🤖 ErosGest AI pronto! Posso ajudar com:\n"
                              "• Cadastrar produtos (ex: 'adicionar 10 camisetas a R$25 custo')\n"
                              "• Consultar estoque, vendas e finanças\n"
                              "• Calcular impostos e preços de revenda\n"
                              "• Registrar vendas e despesas\n\n"
                              "Configure sua OpenAI API Key acima para respostas inteligentes.", "system")

    def _save_api_key(self):
        key = self.api_entry.get().strip()
        from database.db import set_config
        set_config("openai_api_key", key)
        self._append_message("sistema", "✅ API Key salva com segurança.", "system")

    def _append_message(self, sender, text, tag="assistant"):
        self.chat_text.configure(state="normal")

        if sender == "você":
            self.chat_text.insert(tk.END, f"Você: ", "user")
        elif sender == "sistema":
            self.chat_text.insert(tk.END, f"Sistema: ", "system")
        else:
            self.chat_text.insert(tk.END, f"ErosGest AI: ", "user")

        self.chat_text.insert(tk.END, text + "\n", tag)
        self.chat_text.configure(state="disabled")
        self.chat_text.see(tk.END)

    def _send_message(self):
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self._append_message("você", text, "assistant")
        threading.Thread(target=self._process_message, args=(text,), daemon=True).start()

    def _process_message(self, text):
        try:
            from database.db import get_config, get_products, get_financial_summary, get_all_config
            from modules.ai_assistant import (call_openai_chat, build_context_prompt,
                                               parse_ai_response, parse_product_from_text)

            api_key = self.api_entry.get().strip() or get_config("openai_api_key", "")
            config = get_all_config()
            products = get_products(active_only=True)
            financials = get_financial_summary(30)

            system_prompt = build_context_prompt(config, products, financials)
            self._history.append({"role": "user", "content": text})

            if not api_key:
                result = parse_product_from_text(text)
                if result["success"]:
                    d = result["data"]
                    resp = (f"Identificado: {d['name']} — {d['quantity']} {d['unit']} "
                            f"a R${d['cost_price']:.2f}\n"
                            f"Configure sua OpenAI API Key para respostas completas.")
                else:
                    resp = "Configure sua OpenAI API Key em ⚙️ Configurações para usar o assistente."
                self.after(0, lambda r=resp: self._append_message("ErosGest AI", r, "assistant"))
                return

            response = call_openai_chat(
                self._history[-8:],
                api_key,
                model="gpt-4o-mini",
                system_prompt=system_prompt
            )

            self._history.append({"role": "assistant", "content": response})
            parsed = parse_ai_response(response)
            self.after(0, lambda: self._handle_ai_response(parsed))

            # TTS — fala a resposta se ativado
            if getattr(self, "_tts_enabled", True):
                tts_text = parsed.get("text", response)[:280]
                threading.Thread(target=self._speak, args=(tts_text,), daemon=True).start()

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self._append_message("ErosGest AI", f"Erro: {err_msg}", "error"))

    def _speak(self, text):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 0.9)
            voices = engine.getProperty("voices")
            for v in voices:
                if any(x in v.id.lower() for x in ["brazil","portuguese","pt","claudia","luciana"]):
                    engine.setProperty("voice", v.id); break
            engine.say(text)
            engine.runAndWait()
        except ImportError:
            pass  # pyttsx3 não instalado — silencioso
        except Exception as e:
            logger.debug(f"TTS: {e}")

    def _handle_ai_response(self, parsed):
        if parsed["type"] == "action":
            action = parsed["action"]
            data = parsed.get("data", {})
            text = parsed.get("text", "")

            if text:
                self._append_message("ErosGest AI", text, "assistant")

            if action == "add_product":
                self._execute_add_product(data)
            elif action == "record_sale":
                self._execute_record_sale(data)
            else:
                self._append_message("sistema", f"Ação '{action}' reconhecida mas não implementada nesta versão.", "system")
        else:
            self._append_message("ErosGest AI", parsed["text"], "assistant")

    def _execute_add_product(self, data):
        name = data.get("name", "")
        if not name:
            self._append_message("sistema", "Não consegui identificar o nome do produto.", "error")
            return

        confirm = messagebox.askyesno(
            "Confirmar Cadastro",
            f"Cadastrar produto?\n\n"
            f"Nome: {name}\n"
            f"Quantidade: {data.get('quantity', 0)}\n"
            f"Custo: R$ {data.get('cost_price', 0):.2f}\n"
            f"Venda: R$ {data.get('sale_price', 0):.2f}\n"
            f"Categoria: {data.get('category', 'outros')}"
        )

        if confirm:
            try:
                from database.db import add_product
                pid = add_product(
                    name=name,
                    cost_price=float(data.get("cost_price", 0)),
                    sale_price=float(data.get("sale_price", 0)),
                    quantity=int(data.get("quantity", 0)),
                    category=data.get("category", "outros"),
                    supplier=data.get("supplier", ""),
                    ean=data.get("ean", ""),
                    unit=data.get("unit", "un")
                )
                self._append_message("sistema",
                                     f"✅ Produto '{name}' cadastrado com sucesso (ID: {pid})", "action")
                self.app.refresh_all()
            except Exception as e:
                self._append_message("sistema", f"❌ Erro ao cadastrar: {e}", "error")
        else:
            self._append_message("sistema", "Cadastro cancelado.", "system")

    def _execute_record_sale(self, data):
        self._append_message("sistema",
                              "Para registrar vendas, use a aba 💰 Vendas para maior controle.", "system")

    def _start_voice(self):
        if getattr(self, "_voice_active", False):
            return
        self._voice_active = True
        self.voice_btn.configure(text="⏹", style="Ghost.TButton")
        self._append_message("sistema", "🎤 Aguardando... fale agora", "system")
        threading.Thread(target=self._capture_voice, daemon=True).start()

    def _capture_voice(self):
        try:
            from modules.ai_assistant import VoiceCapture
            vc = VoiceCapture()
            result = vc.capture_once(timeout=7)
            def done():
                self._voice_active = False
                self.voice_btn.configure(text="🎤")
                if result["success"]:
                    self.input_var.set(result["text"])
                    self.input_entry.config(fg=COLORS["text_bright"])
                    self.after(80, self._send_message)
                else:
                    self._append_message("sistema", f"🎤 {result['error']}", "error")
            self.after(0, done)
        except Exception as e:
            self._voice_active = False
            self.after(0, lambda: self._append_message("sistema", f"Erro voz: {e}", "error"))
            self.after(0, lambda: self.voice_btn.configure(text="🎤"))


class FinanceTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._build()

    def _build(self):
        tk.Label(self, text="📈 Financeiro", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(padx=24, pady=(20, 16), anchor="w")

        # Seletor de período
        filter_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        filter_frame.pack(fill="x", padx=24, pady=(0, 12))
        tk.Label(filter_frame, text="Período:", font=FONTS["body"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_muted"]).pack(side="left")
        self.period_var = tk.StringVar(value="30")
        for days, label in [("7", "7 dias"), ("30", "30 dias"), ("90", "3 meses"), ("365", "1 ano")]:
            ttk.Radiobutton(filter_frame, text=label, variable=self.period_var, value=days,
                             command=self.refresh).pack(side="left", padx=8)

        # Cards financeiros
        cards = tk.Frame(self, bg=COLORS["bg_dark"])
        cards.pack(fill="x", padx=24, pady=(0, 16))

        self.c_revenue = MetricCard(cards, "RECEITA BRUTA", "R$ 0,00", color=COLORS["green"])
        self.c_revenue.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.c_cost = MetricCard(cards, "CUSTO (CMV)", "R$ 0,00", color=COLORS["red"])
        self.c_cost.pack(side="left", fill="both", expand=True, padx=6)

        self.c_tax = MetricCard(cards, "IMPOSTOS", "R$ 0,00", color=COLORS["yellow"])
        self.c_tax.pack(side="left", fill="both", expand=True, padx=6)

        self.c_net = MetricCard(cards, "LUCRO LÍQUIDO", "R$ 0,00", color=COLORS["accent_light"])
        self.c_net.pack(side="left", fill="both", expand=True, padx=(6, 0))

        # Simulador de imposto
        sim_card = tk.Frame(self, bg=COLORS["bg_card"],
                             highlightbackground=COLORS["border"], highlightthickness=1)
        sim_card.pack(fill="x", padx=24, pady=(0, 12))
        tk.Label(sim_card, text="🧮 Simulador de Imposto & Preço de Revenda",
                 font=FONTS["sub"], bg=COLORS["bg_card"], fg=COLORS["text_bright"]).pack(
            padx=16, pady=(12, 8), anchor="w")

        sim_row = tk.Frame(sim_card, bg=COLORS["bg_card"])
        sim_row.pack(fill="x", padx=16, pady=(0, 12))

        tk.Label(sim_row, text="Custo R$:", font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left")
        self.sim_cost = tk.Entry(sim_row, width=10,
                                  bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                                  font=FONTS["body"], relief="flat", bd=0,
                                  insertbackground=COLORS["accent_light"])
        self.sim_cost.pack(side="left", ipady=6, ipadx=6)

        tk.Label(sim_row, text="  Margem %:", font=FONTS["body"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(side="left")
        self.sim_margin = tk.Entry(sim_row, width=6,
                                    bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                                    font=FONTS["body"], relief="flat", bd=0,
                                    insertbackground=COLORS["accent_light"])
        self.sim_margin.insert(0, "30")
        self.sim_margin.pack(side="left", ipady=6, ipadx=6)

        ttk.Button(sim_row, text="Calcular", style="Accent.TButton",
                   command=self._simulate_price).pack(side="left", padx=12)

        self.sim_result = tk.Label(sim_card, text="", font=FONTS["body"],
                                    bg=COLORS["bg_card"], fg=COLORS["text_bright"])
        self.sim_result.pack(padx=16, pady=(0, 12), anchor="w")

        # Top produtos
        tk.Label(self, text="Top Produtos por Receita", font=FONTS["sub"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(padx=24, anchor="w")

        top_frame = tk.Frame(self, bg=COLORS["bg_card"],
                              highlightbackground=COLORS["border"], highlightthickness=1)
        top_frame.pack(fill="both", expand=True, padx=24, pady=(8, 16))

        cols = ("product", "qty", "revenue", "profit", "margin")
        self.top_tree = ttk.Treeview(top_frame, columns=cols, show="headings", height=10)
        for col, (label, width) in [
            ("product", ("Produto", 200)), ("qty", ("Qtd Vendida", 100)),
            ("revenue", ("Receita", 100)), ("profit", ("Lucro", 100)), ("margin", ("Margem", 80))
        ]:
            self.top_tree.heading(col, text=label, anchor="w")
            self.top_tree.column(col, width=width, anchor="w")
        self.top_tree.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            from database.db import get_financial_summary, get_top_products, get_config
            days = int(self.period_var.get())
            fin = get_financial_summary(days)
            top = get_top_products(10, days)
            self.after(0, lambda: self._update_ui(fin, top))
        except Exception as e:
            logger.error(f"Finance load: {e}")

    def _update_ui(self, fin, top):
        def fmt(v):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        self.c_revenue.update_value(fmt(fin.get("revenue", 0)))
        cost = fin.get("gross_profit", 0) - fin.get("net_profit", 0) - fin.get("taxes", 0)
        self.c_cost.update_value(fmt(max(0, fin.get("revenue", 0) - fin.get("gross_profit", 0))))
        self.c_tax.update_value(fmt(fin.get("taxes", 0)))
        self.c_net.update_value(fmt(fin.get("net_profit", 0)),
                                 f"Margem: {fin.get('margin_pct', 0):.1f}%")

        self.top_tree.delete(*self.top_tree.get_children())
        for p in top:
            margin = (p["total_profit"] / p["total_revenue"] * 100) if p["total_revenue"] > 0 else 0
            self.top_tree.insert("", tk.END, values=(
                p["product_name"],
                p["total_qty"],
                f"R$ {p['total_revenue']:.2f}",
                f"R$ {p['total_profit']:.2f}",
                f"{margin:.1f}%"
            ))

    def _simulate_price(self):
        try:
            cost = float(self.sim_cost.get().replace(",", "."))
            margin = float(self.sim_margin.get()) / 100
        except ValueError:
            messagebox.showerror("Erro", "Digite valores numéricos válidos")
            return

        try:
            from database.db import get_config
            from workers.price_worker import calculate_taxes
            regime = get_config("tax_regime", "simples_nacional")
            state = get_config("state", "SP")
            simples_rate = float(get_config("simples_rate", "0.04"))

            tax_info = calculate_taxes(cost * (1 + margin), regime, state, simples_rate)
            tax_rate = tax_info["tax_rate"]

            # Preço sugerido com imposto embutido
            suggested = cost * (1 + margin) / (1 - tax_rate)
            lucro_liq = suggested - cost - (suggested * tax_rate)

            result = (
                f"Custo: R${cost:.2f}  |  "
                f"Preço sugerido: R${suggested:.2f}  |  "
                f"Imposto ({regime}): R${suggested * tax_rate:.2f} ({tax_rate*100:.1f}%)  |  "
                f"Lucro líquido: R${lucro_liq:.2f}"
            )
            self.sim_result.config(text=result, fg=COLORS["green"])
        except Exception as e:
            self.sim_result.config(text=f"Erro: {e}", fg=COLORS["red"])


class SettingsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app = app
        self._entries = {}
        self._build()

    def _build(self):
        tk.Label(self, text="⚙️ Configurações", font=FONTS["title"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_bright"]).pack(padx=24, pady=(20, 16), anchor="w")

        # Seção de Tema
        theme_frame = tk.LabelFrame(self, text="🎨 Aparência",
                                     bg=COLORS["bg_card"], fg=COLORS["text_bright"],
                                     font=FONTS["sub"], bd=1, relief="solid",
                                     labelanchor="nw")
        theme_frame.pack(fill="x", padx=24, pady=(0, 12))
        theme_frame.configure(highlightbackground=COLORS["border"])

        theme_row = tk.Frame(theme_frame, bg=COLORS["bg_card"])
        theme_row.pack(fill="x", padx=16, pady=12)
        
        tk.Label(theme_row, text="Tema Atual:", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                 width=20, anchor="w").pack(side="left")
        
        self.theme_label = tk.Label(theme_row, text="🌙 Escuro (Padrão)", 
                                     font=FONTS["sub"], bg=COLORS["bg_card"],
                                     fg=COLORS["accent_light"])
        self.theme_label.pack(side="left", padx=10)
        
        ttk.Button(theme_row, text="☀️ Alternar para Claro", 
                   style="Ghost.TButton", command=self._toggle_theme).pack(side="left")
        
        # Carrega tema atual do banco
        from database.db import get_config
        current_theme = get_config("theme") or "dark"
        if current_theme == "light":
            self.theme_label.config(text="☀️ Claro")

        canvas = tk.Canvas(self, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=24)
        scrollbar.pack(side="right", fill="y")

        sections = [
            ("🏪 Loja", [
                ("store_name", "Nome da Loja"),
            ]),
            ("💰 Tributário", [
                ("tax_regime", "Regime (simples_nacional/lucro_presumido/mei/lucro_real)"),
                ("simples_rate", "Alíquota Simples Nacional (ex: 0.04 = 4%)"),
                ("icms_rate", "Alíquota ICMS (ex: 0.12 = 12%)"),
                ("state", "Estado (SP, RJ, MG...)"),
                ("default_margin", "Margem padrão (ex: 0.30 = 30%)"),
            ]),
            ("🔑 API Keys", [
                ("openai_api_key", "OpenAI API Key (sk-...)"),
                ("serpapi_key", "SerpAPI Key (busca de preços)"),
                ("assemblyai_key", "AssemblyAI Key (transcrição de voz)"),
            ]),
            ("⚙️ Sistema", [
                ("worker_interval", "Intervalo do worker em segundos (padrão: 600)"),
                ("low_stock_alert", "Alerta de estoque mínimo (padrão: 5)"),
            ]),
        ]

        from database.db import get_all_config
        config = get_all_config()

        for section_title, fields in sections:
            sec = tk.LabelFrame(scroll_frame, text=section_title,
                                 bg=COLORS["bg_card"], fg=COLORS["text_bright"],
                                 font=FONTS["sub"], bd=1, relief="solid",
                                 labelanchor="nw")
            sec.pack(fill="x", pady=(0, 12))
            sec.configure(highlightbackground=COLORS["border"])

            for key, label in fields:
                row = tk.Frame(sec, bg=COLORS["bg_card"])
                row.pack(fill="x", padx=16, pady=6)
                tk.Label(row, text=label, font=FONTS["small"],
                         bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                         width=45, anchor="w").pack(side="left")
                e = tk.Entry(row, bg=COLORS["input_bg"], fg=COLORS["text_bright"],
                              font=FONTS["mono"], relief="flat", bd=0, width=35,
                              insertbackground=COLORS["accent_light"],
                              show="*" if "key" in key.lower() else "")
                e.pack(side="left", ipady=6, ipadx=8)
                if key in config:
                    e.insert(0, config[key])
                self._entries[key] = e

        ttk.Button(scroll_frame, text="💾 Salvar Configurações",
                   style="Accent.TButton", command=self._save).pack(pady=20)

    def _toggle_theme(self):
        """Alterna entre tema escuro (padrão) e claro"""
        from database.db import get_config, set_config
        
        current_theme = get_config("theme") or "dark"
        new_theme = "light" if current_theme == "dark" else "dark"
        
        # Salva no banco
        set_config("theme", new_theme)
        
        # Aplica o novo tema
        apply_theme(new_theme)
        setup_style()
        
        # Atualiza label do tema
        if new_theme == "dark":
            self.theme_label.config(text="🌙 Escuro (Padrão)", fg=COLORS["accent_light"])
            # Atualiza texto do botão em todas as instâncias seria ideal, 
            # mas como só temos um SettingsTab ativo, atualizamos via recriação
        else:
            self.theme_label.config(text="☀️ Claro", fg=COLORS["accent_light"])
        
        # Atualiza toda a UI
        self.app._apply_current_theme()
        
        messagebox.showinfo("✅ Tema Alterado", 
                          f"Tema {new_theme} aplicado com sucesso!\nO tema escuro é o padrão.")

    def _save(self):
        try:
            from database.db import set_config
            for key, entry in self._entries.items():
                val = entry.get().strip()
                if val:
                    set_config(key, val)
            messagebox.showinfo("✅ Salvo", "Configurações salvas com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))


# ─── APLICAÇÃO PRINCIPAL ─────────────────────────────────────────────────────

class ErosGestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ErosGest AI — Gestão Inteligente")
        self.geometry("1200x760")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg_dark"])

        # Icon
        icon_path = BASE_DIR / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        setup_style()
        self._event_queue = queue.Queue()
        self._build_layout()
        self._start_workers()
        self._poll_events()

        # Refresh inicial
        self.after(500, self.refresh_all)

    def _build_layout(self):
        # Sidebar nav
        sidebar = tk.Frame(self, bg=COLORS["bg_card"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(sidebar, bg=COLORS["bg_card"])
        logo_frame.pack(fill="x", pady=(20, 30))
        tk.Label(logo_frame, text="⚡", font=("Segoe UI", 24),
                 bg=COLORS["bg_card"], fg=COLORS["accent_light"]).pack()
        tk.Label(logo_frame, text="ErosGest AI", font=("Segoe UI", 13, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_bright"]).pack()
        tk.Label(logo_frame, text="Gestão Inteligente", font=FONTS["small"],
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack()

        # Separator
        tk.Frame(sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=(0, 16))

        # Navegação
        nav_items = [
            ("📊", "Dashboard"),
            ("📦", "Estoque"),
            ("💰", "Vendas"),
            ("🤖", "Assistente IA"),
            ("📈", "Financeiro"),
            ("⚙️", "Configurações"),
        ]

        self._nav_btns = {}
        self._nav_frames = {}
        self._active_tab = None

        for icon, label in nav_items:
            btn = tk.Button(sidebar, text=f"  {icon}  {label}",
                            font=FONTS["nav"], bg=COLORS["bg_card"],
                            fg=COLORS["text_muted"], anchor="w",
                            relief="flat", bd=0, padx=16, pady=10,
                            cursor="hand2",
                            command=lambda l=label: self._switch_tab(l))
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["bg_hover"], fg=COLORS["text_bright"]))
            btn.bind("<Leave>", lambda e, b=btn, l=label: self._on_nav_leave(b, l))
            self._nav_btns[label] = btn

        # Worker status
        self.worker_status = tk.Label(sidebar, text="⏸ Worker aguardando",
                                       font=FONTS["small"], bg=COLORS["bg_card"],
                                       fg=COLORS["text_muted"], wraplength=180)
        self.worker_status.pack(side="bottom", padx=16, pady=16)

        # Conteúdo
        self.content = tk.Frame(self, bg=COLORS["bg_dark"])
        self.content.pack(side="left", fill="both", expand=True)

        # Cria as tabs
        self._tabs = {
            "Dashboard": DashboardTab(self.content, self),
            "Estoque": ProductsTab(self.content, self),
            "Vendas": SalesTab(self.content, self),
            "Assistente IA": AssistantTab(self.content, self),
            "Financeiro": FinanceTab(self.content, self),
            "Configurações": SettingsTab(self.content, self),
        }

        self._switch_tab("Dashboard")

    def _on_nav_leave(self, btn, label):
        if label != self._active_tab:
            btn.config(bg=COLORS["bg_card"], fg=COLORS["text_muted"])

    def _switch_tab(self, tab_name):
        if self._active_tab:
            self._tabs[self._active_tab].pack_forget()
            self._nav_btns[self._active_tab].config(
                bg=COLORS["bg_card"], fg=COLORS["text_muted"])

        self._active_tab = tab_name
        self._tabs[tab_name].pack(fill="both", expand=True)
        self._nav_btns[tab_name].config(
            bg=COLORS["accent_dim"], fg=COLORS["text_bright"])

    def _start_workers(self):
        from workers.price_worker import PriceWorker, GamificationWorker

        self._price_worker = PriceWorker(callback=self._on_worker_event)
        self._price_worker.start()

        self._gamification_worker = GamificationWorker(callback=self._on_gamification_event)
        self._gamification_worker.start()

    def _on_worker_event(self, event):
        self._event_queue.put(("worker", event))

    def _on_gamification_event(self, milestone):
        self._event_queue.put(("gamification", milestone))

    def _poll_events(self):
        try:
            while True:
                event_type, data = self._event_queue.get_nowait()
                if event_type == "worker":
                    self._handle_worker_event(data)
                elif event_type == "gamification":
                    self._handle_gamification(data)
        except queue.Empty:
            pass
        self.after(1000, self._poll_events)

    def _handle_worker_event(self, event):
        if event["type"] == "worker_complete":
            self.worker_status.config(
                text=f"✅ Worker: {event['updated']} produtos\n{event['timestamp'][11:16]}",
                fg=COLORS["green"]
            )
            self.after(0, self.refresh_all)
        elif event["type"] == "price_update":
            pass  # silencioso, dados já no banco

    def _handle_gamification(self, milestone):
        m_type = milestone.get("milestone_type", "")
        m_val = milestone.get("milestone_value", 0)

        messages = {
            1: ("🎉 Primeira Venda do Dia!", "Você começou! A primeira venda é sempre especial.", COLORS["green"]),
            5: ("🔥 5 Vendas!", "Você está em chamas! Continue assim!", COLORS["yellow"]),
            10: ("⚡ 10 Vendas!", "Dois dígitos! Sua loja está crescendo!", COLORS["accent_light"]),
            25: ("🚀 25 Vendas!", "Incrível! Você é um revendedor de elite!", COLORS["blue"]),
            50: ("👑 50 Vendas!", "CINQUENTA vendas! Você é imparável!", COLORS["yellow"]),
            100: ("🏆 100 VENDAS!", "CENTENA! Você chegou ao topo! Parabéns!", COLORS["green"]),
        }

        if m_val in messages:
            title, msg, color = messages[m_val]
            self._show_achievement(title, msg, color)

    def _show_achievement(self, title, message, color):
        win = tk.Toplevel(self)
        win.title("🏆 Conquista!")
        win.geometry("380x200")
        win.configure(bg=COLORS["bg_dark"])
        win.attributes("-topmost", True)
        win.resizable(False, False)

        # Centraliza
        win.geometry(f"+{self.winfo_x() + 400}+{self.winfo_y() + 200}")

        tk.Label(win, text=title, font=("Segoe UI", 18, "bold"),
                 bg=COLORS["bg_dark"], fg=color).pack(pady=(24, 8))
        tk.Label(win, text=message, font=FONTS["body"],
                 bg=COLORS["bg_dark"], fg=COLORS["text_main"],
                 wraplength=340).pack()
        ttk.Button(win, text="🎯 Continuar Vendendo!", style="Accent.TButton",
                   command=win.destroy).pack(pady=20)

        win.after(8000, lambda: win.destroy() if win.winfo_exists() else None)

    def check_gamification(self):
        """Verifica marcos após nova venda"""
        from workers.price_worker import GamificationWorker
        threading.Thread(target=self._check_gamification_bg, daemon=True).start()

    def _check_gamification_bg(self):
        try:
            from database.db import get_recent_milestones
            milestones = get_recent_milestones(minutes=3)  # últimos 3 min
            for m in milestones:
                self._event_queue.put(("gamification", m))
        except Exception:
            pass

    def refresh_all(self):
        """Refresh de todas as abas"""
        for name, tab in self._tabs.items():
            if hasattr(tab, "refresh"):
                tab.refresh()

    def _apply_current_theme(self):
        """Aplica o tema atual a todos os widgets da aplicação"""
        from database.db import get_config
        
        # Carrega tema do banco ou usa padrão escuro
        theme_name = get_config("theme") or "dark"
        apply_theme(theme_name)
        setup_style()
        
        # Atualiza cores de fundo da janela principal
        self.configure(bg=COLORS["bg_dark"])
        
        # Atualiza sidebar
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                self._update_widget_colors(widget)
        
        # Refresh nas tabs para aplicar novas cores
        self.refresh_all()

    def _update_widget_colors(self, container):
        """Atualiza recursivamente as cores dos widgets"""
        try:
            if hasattr(container, 'configure'):
                # Tenta atualizar background se for um widget que suporta
                if isinstance(container, (tk.Frame, tk.LabelFrame)):
                    container.configure(bg=COLORS["bg_card"] if container.cget('bg') != COLORS["bg_dark"] else COLORS["bg_dark"])
            
            # Recursão para filhos
            for child in container.winfo_children():
                self._update_widget_colors(child)
        except Exception:
            pass  # Ignora erros em widgets que não suportam certas configurações

    def on_close(self):
        self._price_worker.stop()
        self._gamification_worker.stop()
        self.destroy()


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

def main():
    # Inicializa banco
    from database.db import init_database
    init_database()
    logger.info("ErosGest AI iniciando...")

    app = ErosGestApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)

    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("ErosGest AI encerrado")


if __name__ == "__main__":
    main()