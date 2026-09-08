# 🤖 IA Geradora de E-Books Profissionais v4.0

**Gerador completo de e-books de luxo com auto-melhoria usando Groq API (Gratuita)**

## ✨ Features

✅ **Groq API Gratuita** - Sem custos recorrentes (mixtral-8x7b-32768)  
✅ **Pesquisa Trending** - Busca tendências em tempo real via Serper  
✅ **Design Luxuoso** - Dark gold profissional, totalmente responsivo  
✅ **Gráficos Interativos** - Chart.js integrado em cada capítulo  
✅ **Imagens de Alta Qualidade** - Integração com Pexels (fallback automático)  
✅ **Auto-Melhoria** - Sistema aprende com cada geração  
✅ **PDF + HTML Interativo** - Dual output (Playwright + Web)  
✅ **Retry Automático** - Rate limit e error handling robusto  

---

## 🚀 Instalação Rápida

### 1. Clone o repositório
```bash
git clone https://github.com/deusthorjjj/ebook-generator-groq.git
cd ebook-generator-groq
```

### 2. Crie ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure as chaves de API

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite `.env` e adicione suas chaves:

```env
# OBRIGATÓRIO: Groq (Gratuita)
GROQ_API_KEY=gsk_...

# RECOMENDADO: Serper (2500 buscas/mês gratis)
SERPER_API_KEY=...

# RECOMENDADO: Pexels (imagens gratis)
PEXELS_API_KEY=...
```

#### Onde obter as chaves:

| Serviço | Link | Plano Gratuito |
|---------|------|---|
| **Groq** | https://console.groq.com | Unlimited (dentro de rate limits) |
| **Serper** | https://serper.dev | 2.500 buscas/mês |
| **Pexels** | https://www.pexels.com/api | Ilimitado |

### 5. Inicie a API
```bash
python main.py
```

Acesse: **http://localhost:8000**

---

## 📚 Como Usar

### Via API (Recomendado)

#### 1. Gerar E-book com tema automático
```bash
curl -X POST http://localhost:8000/gerar-ebook \
  -H "Content-Type: application/json" \
  -d "{}" \
  --output ebook.pdf
```

#### 2. Gerar E-book com tema customizado
```bash
curl -X POST http://localhost:8000/gerar-ebook \
  -H "Content-Type: application/json" \
  -d '{
    "tema_customizado": "Marketing Digital de Alta Performance",
    "nicho": "Marketing Digital"
  }' \
  --output ebook.pdf
```

#### 3. Pesquisar temas trending agora
```bash
curl http://localhost:8000/trending | python -m json.tool
```

#### 4. Ver histórico de geração
```bash
curl http://localhost:8000/historico | python -m json.tool
```

#### 5. Ver estado de aprendizado da IA
```bash
curl http://localhost:8000/aprendizado | python -m json.tool
```

---

## 🔌 Endpoints

| Método | Endpoint | Descrição | Tempo |
|--------|----------|-----------|-------|
| `GET` | `/` | Homepage | Instant |
| `GET` | `/health` | Status do sistema | Instant |
| `GET` | `/trending` | Temas trending agora | 5-10s |
| `POST` | `/gerar-ebook` | Gera e-book completo | 3-8 min |
| `GET` | `/download/{id}/pdf` | Baixa o PDF | Instant |
| `GET` | `/download/{id}/html` | Visualiza HTML | Instant |
| `GET` | `/ebook/{id}` | Metadados do e-book | Instant |
| `GET` | `/historico` | Lista todos e-books | Instant |
| `GET` | `/aprendizado` | Estado de auto-melhoria | Instant |
| `GET` | `/docs` | Documentação interativa | Instant |

---

## 🧠 Sistema de Auto-Melhoria

A IA aprende a cada geração:

1. **Avalia** o e-book em 6 critérios (qualidade, design, venda, valor, diferenciação, transformação)
2. **Salva** histórico com scores e prompts usados
3. **A partir de 3 gerações**, analisa padrões de sucesso
4. **Evolui** os prompts automaticamente para melhorar
5. **Próximas gerações** incorporam aprendizados → scores aumentam!

```
Geração 1: Score 5.8/10
Geração 2: Score 6.2/10
Geração 3: Score 6.9/10
Geração 4: Score 7.8/10 ✅ APROVADO
Geração 5: Score 8.2/10
Geração 6: Score 8.7/10
```

Consulte `/aprendizado` para ver o progresso em tempo real.

---

## 📁 Estrutura do Projeto

```
ebook-generator-groq/
├── config.py                 # Configuração centralizada
├── groq_client.py           # Cliente Groq com retry logic
├── web_researcher.py        # Pesquisa trending
├── image_service.py         # Busca de imagens
├── ebook_generator.py       # Orquestração principal
├── self_improver.py         # Auto-melhoria e aprendizado
├── html_template.py         # Geração de HTML
├── main.py                  # API FastAPI
├── requirements.txt         # Dependências
├── .env.example             # Variáveis de ambiente
└── output/                  # E-books gerados
    ├── abc123def/
    │   ├── ebook.html
    │   ├── ebook.pdf
    │   └── metadata.json
    └── xyz789uvw/
        ├── ebook.html
        ├── ebook.pdf
        └── metadata.json
```

---

## 🔍 Arquivo de Configuração

### `config.py`

Define todas as variáveis globais:

```python
GROQ_API_KEY = "gsk_..."           # Obrigatório
SERPER_API_KEY = "..."             # Recomendado
PEXELS_API_KEY = "..."             # Recomendado

LOG_LEVEL = "INFO"
MAX_RETRY_ATTEMPTS = 3
TIMEOUT_SECONDS = 60
MAX_TENTATIVAS_MELHORIA = 3        # Quantas vezes refaz se score < 7.5
MIN_SCORE_APROVACAO = 7.5
```

---

## 📊 Exemplo de Saída

```json
{
  "ebook_id": "abc123def456",
  "gerado_em": "2026-09-08T11:30:45.123456",
  "tema": {
    "tema_escolhido": "Marketing Digital de Alta Performance",
    "subtitulo": "O guia definitivo para escalar suas vendas online",
    "nicho": "Marketing Digital",
    "preco_sugerido": "R$ 297",
    "publico_alvo": "Empreendedores e profissionais de marketing"
  },
  "score_final": 8.3,
  "aprovado": true,
  "scores_detalhe": {
    "qualidade_conteudo": 8.5,
    "design_visual": 8.2,
    "potencial_venda": 8.1,
    "valor_percebido": 8.4,
    "diferenciacao": 8.0,
    "transformacao": 8.2
  },
  "pontos_fortes": [
    "Conteúdo profundo e único",
    "Design luxuoso e moderno",
    "Valor claramente justificado"
  ],
  "tamanho_html_kb": 2450,
  "tamanho_pdf_kb": 8920,
  "html_path": "/absolute/path/to/output/abc123def456/ebook.html",
  "pdf_path": "/absolute/path/to/output/abc123def456/ebook.pdf"
}
```

---

## ⚙️ Configuração Avançada

### Aumentar Max Tokens (mais conteúdo)

Em `ebook_generator.py`, linha ~120:

```python
max_tokens=2000  # Aumentar para 3000 (custos maiores)
```

### Mudar Modelo Groq

Em `config.py`:

```python
GROQ_MODEL = "mixtral-8x7b-32768"  # Padrão (rápido)
# Opções: "mixtral-8x7b-32768", "llama-2-70b-chat", "gemma-7b-it"
```

### Disable Playwright PDF

Se tiver erro com Chrome, remova o PDF (apenas HTML):

Em `ebook_generator.py`, linha ~280:

```python
# pdf = await self._renderizar_pdf(html)  # Comentar
pdf = b"PDF_UNAVAILABLE"  # Usar fallback
```

---

## 🐛 Troubleshooting

### Erro: `GROQ_API_KEY não definida`
```bash
# Verifique se .env existe e tem GROQ_API_KEY
cat .env | grep GROQ
```

### Erro: `Playwright chromium not found`
```bash
playwright install chromium --with-deps
```

### Erro: `Rate limit reached`
O sistema retry automaticamente após 2^n segundos. Aguarde ou:
- Aumentar `MAX_RETRY_ATTEMPTS` em config.py
- Usar Groq com tier pago (mais rate limit)

### E-book vazio ou com texto "N/A"
Pode ser timeout do Groq. Tente novamente - o sistema tenta 3x.

### PDF com erro "networkidle"
Aumentar timeout em `ebook_generator.py`:
```python
wait_until="load"  # Ao invés de "networkidle"
```

---

## 📈 Performance

| Operação | Tempo | Custo |
|----------|-------|-------|
| Pesquisa trending | 5-10s | Serper (free) |
| Gerar estrutura | 15-20s | Groq (free) |
| Escrever 7 capítulos | 90-120s | Groq (free) |
| Gerar gráficos | 30-40s | Groq (free) |
| Buscar imagens | 20-30s | Pexels (free) |
| Renderizar PDF | 10-15s | Playwright (local) |
| Auto-avaliar | 20-30s | Groq (free) |
| **TOTAL** | **3-8 min** | **100% GRATUITO** |

---

## 🎉 Pronto para começar?

```bash
# 1. Instale dependências
pip install -r requirements.txt
playwright install chromium

# 2. Configure .env
cp .env.example .env
# Edite e adicione GROQ_API_KEY

# 3. Inicie
python main.py

# 4. Gere seu primeiro e-book
curl -X POST http://localhost:8000/gerar-ebook \
  -H "Content-Type: application/json" \
  -d "{}" \
  --output primeiro_ebook.pdf
```

---

**Versão**: 4.0.0  
**Status**: ✅ 100% Funcional  
**Licença**: MIT
