"""
ErosGest AI — Módulo de IA Real
Integração com OpenAI GPT para assistente de voz/chat
STT via SpeechRecognition (offline) ou AssemblyAI (online)
"""
import json
import logging
import re
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


def call_openai_chat(messages, api_key, model="gpt-4o-mini", max_tokens=1000, system_prompt=None):
    """
    Chamada real à API da OpenAI
    SDK: https://platform.openai.com/docs/api-reference
    """
    if not api_key:
        raise ValueError("OpenAI API Key não configurada. Acesse Configurações → API Keys.")

    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    payload = json.dumps({
        "model": model,
        "messages": full_messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            err = json.loads(error_body)
            msg = err.get("error", {}).get("message", error_body)
        except Exception:
            msg = error_body
        raise RuntimeError(f"OpenAI API erro {e.code}: {msg}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Sem conexão com OpenAI: {e.reason}")


def call_gemini_chat(message, api_key, model="gemini-1.5-flash", image_data=None):
    """
    Google Gemini API com suporte a imagens
    https://ai.google.dev/api
    """
    if not api_key:
        raise ValueError("Gemini API Key não configurada.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # Constrói o conteúdo da mensagem (texto + imagem opcional)
    parts = []
    if image_data:
        # Imagem em base64
        parts.append({"inline_data": {"mime_type": "image/png", "data": image_data}})
    parts.append({"text": message})
    
    payload = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1000}
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"Gemini API erro {e.code}: {error_body}")


SYSTEM_PROMPT_TEMPLATE = """Você é o assistente ErosGest AI, especializado em gestão de revendas.

CONTEXTO DO USUÁRIO:
- Loja: {store_name}
- Regime tributário: {tax_regime}
- Estado: {state}

ESTOQUE ATUAL (top 10 por quantidade):
{stock_summary}

RESUMO FINANCEIRO (últimos 30 dias):
{financial_summary}

INSTRUÇÕES:
- Responda SEMPRE em português brasileiro, de forma direta e prática
- Para cadastrar produto, retorne JSON no formato: {"action": "add_product", "data": {...}}
- Para registrar venda: {"action": "record_sale", "data": {...}}
- Para consulta: responda em linguagem natural
- Para dúvidas fiscais: dê orientações gerais e sempre recomende consultar contador
- Seja objetivo: máximo 3 parágrafos para respostas livres

AÇÕES DISPONÍVEIS VIA COMANDO:
- Cadastrar produto: nome, quantidade, preço de custo, preço de venda, categoria
- Registrar venda: produto, quantidade, preço
- Consultar estoque: produto específico ou lista geral
- Relatório financeiro: receita, lucro, impostos
- Sugestão de preço: baseada em custo + mercado"""


def build_context_prompt(config: dict, products: list, financials: dict) -> str:
    """Constrói o prompt de contexto com dados reais do banco"""
    stock_lines = []
    for p in products[:10]:
        line = f"- {p['name']}: {p['quantity']} {p['unit']} | Custo: R${p['cost_price']:.2f} | Venda: R${p['sale_price']:.2f}"
        if p['quantity'] <= p.get('min_quantity', 5):
            line += " ⚠️ ESTOQUE BAIXO"
        stock_lines.append(line)

    fin = financials
    fin_summary = (
        f"Receita: R${fin.get('revenue', 0):.2f} | "
        f"Lucro bruto: R${fin.get('gross_profit', 0):.2f} | "
        f"Impostos: R${fin.get('taxes', 0):.2f} | "
        f"Despesas: R${fin.get('expenses', 0):.2f} | "
        f"Lucro líquido: R${fin.get('net_profit', 0):.2f} | "
        f"Margem: {fin.get('margin_pct', 0):.1f}%"
    )

    return SYSTEM_PROMPT_TEMPLATE.format(
        store_name=config.get("store_name", "Minha Loja"),
        tax_regime=config.get("tax_regime", "simples_nacional"),
        state=config.get("state", "SP"),
        stock_summary="\n".join(stock_lines) if stock_lines else "Nenhum produto cadastrado",
        financial_summary=fin_summary
    )


def parse_ai_response(response_text: str) -> dict:
    """
    Analisa a resposta da IA e extrai ação estruturada se houver
    Retorna: {"type": "action"|"text", "action": str, "data": dict, "text": str}
    """
    if not response_text or not isinstance(response_text, str):
        return {"type": "text", "text": "Resposta vazia ou inválida da IA."}
    
    text = response_text.strip()

    # Tenta encontrar JSON com action - padrão mais flexível
    try:
        # Primeiro tenta parsear o texto inteiro como JSON
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "action" in parsed:
            data_val = parsed.get("data")
            if not isinstance(data_val, dict):
                data_val = {}
            action_val = parsed.get("action")
            if action_val and isinstance(action_val, str):
                return {
                    "type": "action",
                    "action": action_val,
                    "data": data_val,
                    "text": f"Executando: {action_val}"
                }
    except (json.JSONDecodeError, TypeError, KeyError, ValueError):
        pass

    # Tenta extrair JSON de dentro do texto (padrão mais abrangente)
    # Procura por { seguido de conteúdo até } correspondente
    start = text.find('{')
    if start != -1:
        # Encontra o fechamento correspondente
        depth = 0
        end = -1
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        
        if end != -1:
            json_str = text[start:end]
            try:
                parsed = json.loads(json_str)
                if isinstance(parsed, dict) and "action" in parsed:
                    data_val = parsed.get("data")
                    if not isinstance(data_val, dict):
                        data_val = {}
                    action_val = parsed.get("action")
                    if action_val and isinstance(action_val, str):
                        display_text = (text[:start] + text[end:]).strip()
                        return {
                            "type": "action",
                            "action": action_val,
                            "data": data_val,
                            "text": display_text or f"Executando: {action_val}"
                        }
            except (json.JSONDecodeError, TypeError, KeyError, ValueError):
                pass

    # Se não encontrou ação válida, retorna como texto normal
    return {"type": "text", "text": text}


def parse_product_from_text(text: str, api_key: str = None) -> dict:
    """
    Extrai dados estruturados de produto a partir de texto livre
    Usa IA se disponível, regex como fallback
    """
    if api_key:
        try:
            prompt = f"""Extraia dados do produto do texto abaixo e retorne SOMENTE um JSON válido.
Schema obrigatório:
{{
  "name": "nome do produto (string)",
  "quantity": número inteiro,
  "cost_price": número decimal,
  "sale_price": número decimal (0 se não mencionado),
  "category": "categoria (string, default 'outros')",
  "supplier": "fornecedor (string, default '')",
  "ean": "código EAN (string, default '')",
  "unit": "unidade: un/kg/lt/cx (default 'un')"
}}

Texto: "{text}"

Retorne APENAS o JSON, sem explicações."""

            response = call_openai_chat(
                [{"role": "user", "content": prompt}],
                api_key,
                max_tokens=300
            )

            # Remove possíveis backticks
            clean = re.sub(r'```(?:json)?', '', response).strip().rstrip('`').strip()
            data = json.loads(clean)

            # Validação de schema
            required = ["name", "quantity", "cost_price"]
            for field in required:
                if field not in data:
                    raise ValueError(f"Campo obrigatório ausente: {field}")

            data["quantity"] = int(data.get("quantity", 0))
            data["cost_price"] = float(data.get("cost_price", 0))
            data["sale_price"] = float(data.get("sale_price", 0))

            return {"success": True, "data": data}

        except Exception as e:
            logger.warning(f"IA falhou no parse, usando regex: {e}")

    # Fallback: regex básico
    result = {
        "name": "",
        "quantity": 0,
        "cost_price": 0.0,
        "sale_price": 0.0,
        "category": "outros",
        "supplier": "",
        "ean": "",
        "unit": "un"
    }

    # Nome: primeira parte antes de números
    name_match = re.match(r'^([a-zA-ZÀ-ú\s]+)', text.strip())
    if name_match:
        result["name"] = name_match.group(1).strip()

    # Quantidades
    qty_match = re.search(r'(\d+)\s*(?:unidade[s]?|un|peça[s]?|caixa[s]?|kg|lt)', text, re.I)
    if qty_match:
        result["quantity"] = int(qty_match.group(1))
    elif re.search(r'\d+', text):
        nums = re.findall(r'\d+', text)
        if nums:
            result["quantity"] = int(nums[0])

    # Preços (R$ ou valores com vírgula/ponto)
    price_matches = re.findall(r'R?\$?\s*(\d+(?:[.,]\d{1,2})?)', text)
    prices = []
    for p in price_matches:
        try:
            prices.append(float(p.replace(',', '.')))
        except ValueError:
            pass

    if len(prices) >= 2:
        result["cost_price"] = min(prices[:2])
        result["sale_price"] = max(prices[:2])
    elif len(prices) == 1:
        result["cost_price"] = prices[0]

    if not result["name"]:
        return {"success": False, "error": "Não foi possível identificar o produto", "data": result}

    return {"success": True, "data": result}


class VoiceCapture:
    """
    Captura de voz real usando SpeechRecognition
    Fallback: AssemblyAI para maior precisão
    """
    def __init__(self, assemblyai_key=None):
        self.assemblyai_key = assemblyai_key
        self._sr_available = False
        self._check_dependencies()

    def _check_dependencies(self):
        try:
            import speech_recognition as sr
            self._sr_available = True
            self._sr = sr
        except ImportError:
            logger.info("SpeechRecognition não instalado. Instale: pip install SpeechRecognition PyAudio")

    def is_available(self) -> bool:
        return self._sr_available

    def capture_once(self, timeout=5, language="pt-BR") -> dict:
        """Captura e transcreve um comando de voz"""
        if not self._sr_available:
            return {"success": False, "error": "Microfone não disponível. Instale: pip install SpeechRecognition PyAudio"}

        sr = self._sr
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True

        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Aguardando fala...")
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=15)

            # Tenta Google STT (gratuito, sem chave)
            try:
                text = recognizer.recognize_google(audio, language=language)
                return {"success": True, "text": text, "source": "Google STT"}
            except sr.UnknownValueError:
                return {"success": False, "error": "Não entendi o que foi dito"}
            except sr.RequestError as e:
                logger.warning(f"Google STT falhou: {e}")

            # Fallback: Sphinx offline (se instalado)
            try:
                text = recognizer.recognize_sphinx(audio)
                return {"success": True, "text": text, "source": "Sphinx (offline)"}
            except Exception:
                pass

            return {"success": False, "error": "STT indisponível no momento"}

        except sr.WaitTimeoutError:
            return {"success": False, "error": "Nenhuma fala detectada (timeout)"}
        except Exception as e:
            return {"success": False, "error": f"Erro no microfone: {str(e)}"}

    def transcribe_assemblyai(self, audio_file_path: str) -> dict:
        """Transcrição de arquivo de áudio via AssemblyAI (maior precisão)"""
        if not self.assemblyai_key:
            return {"success": False, "error": "AssemblyAI key não configurada"}

        try:
            # Upload do arquivo
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()

            upload_req = urllib.request.Request(
                "https://api.assemblyai.com/v2/upload",
                data=audio_data,
                headers={
                    "authorization": self.assemblyai_key,
                    "content-type": "application/octet-stream"
                },
                method="POST"
            )
            with urllib.request.urlopen(upload_req, timeout=30) as resp:
                upload_data = json.loads(resp.read().decode())
            audio_url = upload_data["upload_url"]

            # Solicita transcrição
            transcribe_req = urllib.request.Request(
                "https://api.assemblyai.com/v2/transcript",
                data=json.dumps({
                    "audio_url": audio_url,
                    "language_code": "pt"
                }).encode(),
                headers={
                    "authorization": self.assemblyai_key,
                    "content-type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(transcribe_req, timeout=15) as resp:
                trans_data = json.loads(resp.read().decode())
            transcript_id = trans_data["id"]

            # Polling até completar
            import time
            for _ in range(30):
                poll_req = urllib.request.Request(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers={"authorization": self.assemblyai_key}
                )
                with urllib.request.urlopen(poll_req, timeout=10) as resp:
                    result = json.loads(resp.read().decode())

                if result["status"] == "completed":
                    return {"success": True, "text": result["text"], "source": "AssemblyAI"}
                elif result["status"] == "error":
                    return {"success": False, "error": result.get("error", "AssemblyAI erro")}
                time.sleep(2)

            return {"success": False, "error": "AssemblyAI timeout"}

        except Exception as e:
            return {"success": False, "error": f"AssemblyAI: {str(e)}"}
