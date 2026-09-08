"""
config.py
Configuracao centralizada da aplicacao.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Chaves de API
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Validacoes
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY nao definida. Configure em .env ou variavel de ambiente")

# Configuracoes
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "60"))
MAX_TENTATIVAS_MELHORIA = 3
MIN_SCORE_APROVACAO = 7.5

# Caminhos
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

PROMPTS_DIR = Path("prompts")
PROMPTS_DIR.mkdir(exist_ok=True)

# URLs e endpoints
GROQ_API_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "mixtral-8x7b-32768"  # Modelo gratis da Groq

# Configuracao de Groq
GROQ_CONFIG = {
    "api_key": GROQ_API_KEY,
    "base_url": GROQ_API_URL,
    "model": GROQ_MODEL,
    "timeout": TIMEOUT_SECONDS,
    "max_retries": MAX_RETRY_ATTEMPTS,
}

print("")
print("=" * 70)
print("  ✅ CONFIGURACAO CARREGADA COM SUCESSO")
print("=" * 70)
print(f"  📌 Groq API: {GROQ_MODEL}")
print(f"  📌 Serper: {'✅ Ativo' if SERPER_API_KEY else '⚠️  Desativado'}")
print(f"  📌 Pexels: {'✅ Ativo' if PEXELS_API_KEY else '⚠️  Desativado (placeholder)'}")
print(f"  📌 Diretorio de saida: {OUTPUT_DIR.absolute()}")
print("=" * 70)
print("")
