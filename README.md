# ⚡ ErosGest AI — Gestão Inteligente para Revendedores

> **"Venda mais, gaste menos, decida melhor."**

---

## 🚀 Início Rápido

### Executar diretamente (sem build)
```bash
pip install -r requirements.txt
python main.py
```

### Gerar EXE para Windows
```batch
# Clique duas vezes em build.bat
# O EXE será gerado em dist\ErosGest AI.exe
```

---

## 📁 Estrutura do Projeto

```
erosgest/
├── main.py                    # Aplicação principal (GUI tkinter)
├── icon.ico                   # Ícone do programa
├── create_icon.py             # Gerador do ícone
├── build.bat                  # Script de build → .exe
├── requirements.txt           # Dependências
├── database/
│   ├── __init__.py
│   └── db.py                  # SQLite com transações ACID
├── modules/
│   ├── __init__.py
│   └── ai_assistant.py        # OpenAI + STT + Gemini fallback
└── workers/
    ├── __init__.py
    └── price_worker.py        # Worker 10min + circuit breaker + impostos
```

---

## 🔧 Funcionalidades Reais

### 1. Dashboard Analítico
- Receita, lucro, margem, vendas dos últimos 30 dias
- Gráfico de vendas diárias (canvas nativo)
- Alertas de estoque baixo em tempo real

### 2. Gestão de Estoque (Produtos)
- CRUD completo com validações
- Pesquisa e filtro por categoria
- Estoque mínimo configurável por produto
- Histórico de preços de mercado

### 3. Registro de Vendas
- Venda rápida com seleção de produto
- Suporte a múltiplos métodos de pagamento
- Cálculo automático de lucro e impostos
- Sistema de gamificação com marcos reais

### 4. Assistente IA (GPT-4)
- Chat contextual com dados reais do estoque
- Cadastro de produtos por voz ou texto
- Captura por microfone (SpeechRecognition)
- Executa ações reais no sistema

### 5. Controle Financeiro
- Receita, CMV, impostos, lucro líquido
- Simulador de preço de revenda + impostos
- Top produtos por receita e margem
- Exportação de relatórios

### 6. Worker de Preços (Background)
- Roda a cada 10 minutos automaticamente
- Busca preços reais no Mercado Livre (API pública)
- Compara com Google Shopping via SerpAPI
- Circuit breaker + retry exponencial
- Cache local para evitar rate limits

### 7. Gamificação Real
- 1ª venda, 5, 10, 25, 50, 100 vendas/dia
- Pop-up com animação e mensagem motivacional
- Marcos persistidos no banco de dados

---

## 🔑 Configuração de API Keys

Configure na aba **⚙️ Configurações**:

| Serviço | Para que serve | Link |
|---------|---------------|------|
| **OpenAI** | Assistente IA completo | [platform.openai.com](https://platform.openai.com/api-keys) |
| **SerpAPI** | Comparação de preços (Google Shopping) | [serpapi.com](https://serpapi.com/manage-api-key) |
| **AssemblyAI** | Transcrição de voz de alta qualidade | [assemblyai.com](https://www.assemblyai.com/) |

> **O programa funciona sem API Keys**, mas com funcionalidade reduzida.
> O Mercado Livre não requer chave para busca básica de preços.

---

## 💰 Tributário

Regimes suportados:
- **Simples Nacional** — alíquota única configurável
- **Lucro Presumido** — ICMS + PIS + COFINS + IRPJ + CSLL
- **MEI** — DAS fixo mensal
- **Lucro Real** — PIS/COFINS não-cumulativo

> ⚠️ Estimativas tributárias. Sempre valide com seu contador.

---

## 🗃️ Banco de Dados

- **SQLite** local: `C:\Users\[usuário]\.erosgest\erosgest.db`
- WAL mode para performance e concorrência
- Logs de auditoria completos
- Backup: copie o arquivo `.db`
- Migração para PostgreSQL: substitua `sqlite3` por `psycopg2` em `database/db.py`

---

## 📞 Suporte e Extensões

Para integrar com sistemas existentes:
- **API REST**: adicione `fastapi` + `uvicorn`
- **PostgreSQL/Supabase**: altere `get_connection()` em `db.py`
- **WhatsApp**: adicione `whatsapp-web.py` ou Twilio
- **NFC/Leitor de código**: altere o campo EAN para captura por USB HID
