"""
ErosGest AI — Background Worker
Worker real que roda a cada 10 minutos buscando produtos e comparando preços
"""
import threading
import time
import logging
import json
import re
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

# Adiciona o diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker real para APIs externas"""
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time = None
        self.state = "closed"  # closed=normal, open=blocked, half-open=testing

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise RuntimeError("Circuit breaker OPEN — API temporariamente bloqueada")

        try:
            result = func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(f"Circuit breaker OPENED após {self.failure_count} falhas")
            raise


def exponential_backoff(func, max_retries=3, base_delay=1.0):
    """Retry com backoff exponencial real"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Tentativa {attempt+1} falhou: {e}. Aguardando {delay:.1f}s...")
            time.sleep(delay)


def fetch_mercadolivre_prices(product_name, api_key=None):
    """
    Busca preços reais no Mercado Livre via API oficial
    https://developers.mercadolivre.com.br/
    Retorna lista de ofertas reais
    """
    results = []
    try:
        # Endpoint oficial da API pública do ML (sem autenticação para busca básica)
        encoded_name = urllib.parse.quote(product_name)
        url = f"https://api.mercadolibre.com/sites/MLB/search?q={encoded_name}&limit=5"

        req = urllib.request.Request(url, headers={
            "User-Agent": "ErosGest-AI/1.0",
            "Accept": "application/json"
        })

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        for item in data.get("results", [])[:5]:
            results.append({
                "source": "Mercado Livre",
                "title": item.get("title", ""),
                "price": item.get("price", 0),
                "url": item.get("permalink", ""),
                "image_url": item.get("thumbnail", ""),
                "available": item.get("available_quantity", 0) > 0,
                "condition": item.get("condition", ""),
            })

    except urllib.error.HTTPError as e:
        logger.warning(f"ML API HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        logger.warning(f"ML API conexão falhou: {e.reason}")
    except Exception as e:
        logger.warning(f"ML API erro: {e}")

    return results


def fetch_serpapi_prices(product_name, api_key):
    """
    Busca preços via SerpAPI (Google Shopping)
    Requer chave em https://serpapi.com
    """
    if not api_key:
        return []

    results = []
    try:
        params = urllib.parse.urlencode({
            "q": product_name,
            "engine": "google_shopping",
            "api_key": api_key,
            "gl": "br",
            "hl": "pt",
            "num": "5"
        })
        url = f"https://serpapi.com/search?{params}"

        req = urllib.request.Request(url, headers={"User-Agent": "ErosGest-AI/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        for item in data.get("shopping_results", [])[:5]:
            price_str = item.get("price", "0")
            # Remove R$, pontos de milhar, troca vírgula por ponto
            price_clean = re.sub(r'[^\d,.]', '', price_str).replace(',', '.')
            try:
                price = float(price_clean)
            except ValueError:
                price = 0

            results.append({
                "source": item.get("source", "Google Shopping"),
                "title": item.get("title", ""),
                "price": price,
                "url": item.get("link", ""),
                "image_url": item.get("thumbnail", ""),
                "available": True,
                "condition": "new",
            })

    except urllib.error.HTTPError as e:
        logger.warning(f"SerpAPI HTTP {e.code}: {e.reason}")
        if e.code == 401:
            logger.error("SerpAPI: Chave inválida ou expirada")
    except Exception as e:
        logger.warning(f"SerpAPI erro: {e}")

    return results


def calculate_suggested_price(cost_price, market_prices, margin_pct=0.30, tax_rate=0.04):
    """
    Calcula preço sugerido baseado no mercado real e custos reais
    """
    if not market_prices:
        # Sem dados de mercado: aplica margem simples + imposto
        base = cost_price * (1 + margin_pct)
        with_tax = base / (1 - tax_rate)
        return round(with_tax, 2)

    valid_prices = [p["price"] for p in market_prices if p["price"] > 0]
    if not valid_prices:
        base = cost_price * (1 + margin_pct)
        return round(base / (1 - tax_rate), 2)

    avg_market = sum(valid_prices) / len(valid_prices)
    min_market = min(valid_prices)

    # Estratégia: ligeiramente abaixo da média, mas com margem mínima
    cost_with_tax = cost_price / (1 - tax_rate)
    min_viable = cost_with_tax * (1 + margin_pct * 0.7)  # margem mínima aceitável
    target = avg_market * 0.95  # 5% abaixo da média

    suggested = max(min_viable, min(target, avg_market))
    return round(suggested, 2)


class PriceWorker:
    """
    Worker real que roda em background a cada 10 minutos
    Busca preços, compara, salva histórico e notifica
    """
    def __init__(self, callback=None):
        self.callback = callback  # função chamada com atualizações
        self.running = False
        self.thread = None
        self.interval = 600  # 10 minutos
        self.circuit_breakers = {
            "mercadolivre": CircuitBreaker(failure_threshold=3, recovery_timeout=120),
            "serpapi": CircuitBreaker(failure_threshold=3, recovery_timeout=300),
        }
        self.last_run = None
        self.stats = {"runs": 0, "products_updated": 0, "errors": 0}

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True, name="PriceWorker")
        self.thread.start()
        logger.info("PriceWorker iniciado")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("PriceWorker parado")

    def _run_loop(self):
        # Primeira execução após 30s (deixa o app carregar)
        time.sleep(30)
        while self.running:
            try:
                self._execute_run()
            except Exception as e:
                logger.error(f"PriceWorker erro no ciclo: {e}", exc_info=True)
                self.stats["errors"] += 1

            # Aguarda o intervalo (verifica a cada 10s se deve parar)
            elapsed = 0
            while self.running and elapsed < self.interval:
                time.sleep(10)
                elapsed += 10

    def _execute_run(self):
        from database.db import get_products_needing_price_update, get_config
        
        self.last_run = datetime.now()
        self.stats["runs"] += 1
        logger.info(f"PriceWorker: Iniciando ciclo #{self.stats['runs']}")

        serpapi_key = get_config("serpapi_key", "")
        # Usa a nova função para pegar apenas produtos que precisam de atualização
        products = get_products_needing_price_update(limit=20)
        
        if not products:
            logger.info("Nenhum produto precisa de atualização de preço no momento")
            return

        updated = 0
        for product in products[:20]:  # limita para não exceder rate limits
            if not self.running:
                break
            try:
                self._update_product_prices(product, serpapi_key)
                updated += 1
                time.sleep(2)  # Rate limiting ético: 2s entre requests
            except Exception as e:
                logger.warning(f"Produto '{product['name']}': {e}")

        self.stats["products_updated"] += updated
        logger.info(f"PriceWorker: Ciclo #{self.stats['runs']} concluído. {updated} produtos atualizados.")

        if self.callback:
            self.callback({
                "type": "worker_complete",
                "updated": updated,
                "timestamp": self.last_run.isoformat()
            })

    def _update_product_prices(self, product, serpapi_key):
        from database.db import update_product_price_info

        product_name = product["name"]
        market_prices = []

        # Tenta Mercado Livre (API pública gratuita)
        try:
            ml_prices = self.circuit_breakers["mercadolivre"].call(
                fetch_mercadolivre_prices, product_name
            )
            market_prices.extend(ml_prices)
        except RuntimeError as e:
            logger.debug(f"ML circuit breaker: {e}")
        except Exception as e:
            logger.debug(f"ML erro para '{product_name}': {e}")

        # Tenta SerpAPI se tiver chave
        if serpapi_key:
            try:
                serp_prices = self.circuit_breakers["serpapi"].call(
                    fetch_serpapi_prices, product_name, serpapi_key
                )
                market_prices.extend(serp_prices)
            except RuntimeError as e:
                logger.debug(f"SerpAPI circuit breaker: {e}")

        if not market_prices:
            return

        # Salva o melhor preço encontrado usando a nova função
        best_price = None
        best_source = None
        best_url = None
        
        for p in market_prices:
            if p["price"] > 0 and (best_price is None or p["price"] < best_price):
                best_price = p["price"]
                best_source = p["source"]
                best_url = p.get("url", "")
        
        if best_price:
            update_product_price_info(product["id"], best_source, best_price, best_url)

        # Calcula preço sugerido
        tax_rate = 0.04
        try:
            from database.db import get_config
            tax_rate = float(get_config("simples_rate", "0.04"))
        except Exception:
            pass

        suggested = calculate_suggested_price(
            product["cost_price"],
            market_prices,
            margin_pct=0.30,
            tax_rate=tax_rate
        )

        if self.callback:
            self.callback({
                "type": "price_update",
                "product_id": product["id"],
                "product_name": product_name,
                "market_prices": market_prices[:3],
                "suggested_price": suggested,
                "current_price": product["sale_price"],
            })


class GamificationWorker:
    """Monitor de marcos e gatilhos de gamificação"""
    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.thread = None
        self.notified_milestones = set()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True, name="GamificationWorker")
        self.thread.start()

    def stop(self):
        self.running = False

    def _monitor(self):
        while self.running:
            try:
                from database.db import get_recent_milestones
                milestones = get_recent_milestones(minutes=6)  # últimos 6 minutos
                for m in milestones:
                    key = f"{m['milestone_type']}_{m['milestone_value']}_{m['achieved_at'][:10]}"
                    if key not in self.notified_milestones:
                        self.notified_milestones.add(key)
                        if self.callback:
                            self.callback(m)
            except Exception as e:
                logger.debug(f"Gamification monitor: {e}")
            time.sleep(15)


def calculate_taxes(sale_price, regime="simples_nacional", state="SP",
                    simples_rate=0.04, icms_rate=0.12, pis_rate=0.0065, cofins_rate=0.03):
    """
    Cálculo real de impostos baseado no regime tributário
    Fonte: Receita Federal - tabelas oficiais
    """
    if regime == "simples_nacional":
        # Simples Nacional: alíquota única sobre faturamento
        tax = sale_price * simples_rate
        return {
            "regime": "Simples Nacional",
            "total_tax": round(tax, 2),
            "breakdown": {
                "Simples Nacional": round(tax, 2)
            },
            "tax_rate": simples_rate,
            "note": "Alíquota média. Consulte contador para cálculo exato por faixa de faturamento."
        }

    elif regime == "lucro_presumido":
        # Lucro Presumido: ICMS + PIS + COFINS + IRPJ + CSLL
        icms = sale_price * icms_rate
        pis = sale_price * pis_rate
        cofins = sale_price * cofins_rate
        irpj = sale_price * 0.048  # 8% presunção × 15% IRPJ = 1.2%, + adicional
        csll = sale_price * 0.0288  # 12% presunção × 9% CSLL
        total = icms + pis + cofins + irpj + csll
        return {
            "regime": "Lucro Presumido",
            "total_tax": round(total, 2),
            "breakdown": {
                f"ICMS ({state})": round(icms, 2),
                "PIS": round(pis, 2),
                "COFINS": round(cofins, 2),
                "IRPJ (estimado)": round(irpj, 2),
                "CSLL (estimado)": round(csll, 2),
            },
            "tax_rate": total / sale_price if sale_price > 0 else 0,
            "note": "Estimativa. Valores reais dependem do faturamento acumulado e deduções."
        }

    elif regime == "mei":
        # MEI: DAS fixo mensal, não por venda
        return {
            "regime": "MEI",
            "total_tax": 0,
            "breakdown": {"DAS MEI": "Valor fixo mensal (não por venda)"},
            "tax_rate": 0,
            "note": "MEI paga DAS fixo mensal. Limite: R$81.000/ano."
        }

    else:  # lucro_real
        icms = sale_price * icms_rate
        pis = sale_price * 0.0165  # regime não-cumulativo
        cofins = sale_price * 0.076
        total = icms + pis + cofins
        return {
            "regime": "Lucro Real",
            "total_tax": round(total, 2),
            "breakdown": {
                f"ICMS ({state})": round(icms, 2),
                "PIS (não-cumulativo)": round(pis, 2),
                "COFINS (não-cumulativo)": round(cofins, 2),
            },
            "tax_rate": total / sale_price if sale_price > 0 else 0,
            "note": "IRPJ/CSLL calculados separadamente sobre lucro real. Consulte contador."
        }
