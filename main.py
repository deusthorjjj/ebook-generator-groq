"""
main.py
API FastAPI para geração de e-books profissionais com IA usando Groq.
"""
import os
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import Response, JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import OUTPUT_DIR, GROQ_API_KEY
from ebook_generator import EbookGenerator
from self_improver import SelfImprover
from web_researcher import WebResearcher

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY não definida!")

# Modelos
class GerarEbookRequest(BaseModel):
    tema_customizado: Optional[str] = Field(None, description="Deixe vazio para IA escolher")
    nicho: Optional[str] = Field(None, description="Nicho específico")

# FastAPI
app = FastAPI(
    title="IA Geradora de E-Books com Groq",
    version="4.0.0",
    description="Gera e-books profissionais de luxo usando Groq (gratuito) + Playwright + Pexels.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instâncias globais
gerador = EbookGenerator()
improver = SelfImprover()
researcher = WebResearcher()

# Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html><head><title>IA E-Book Generator</title>
    <style>
      body{font-family:sans-serif;background:#0a0a0a;color:#d4af37;padding:3rem;text-align:center;}
      h1{font-size:2.5rem;margin-bottom:1rem;}
      a{color:#fff;margin:0 1rem;text-decoration:none;padding:0.5rem 1rem;border:1px solid #d4af37;}
      a:hover{background:#d4af37;color:#0a0a0a;}
      p{color:#888;}
    </style>
    </head><body>
    <h1>🤖 IA Geradora de E-Books</h1>
    <p>Usando Groq API (Gratuita) para máxima performance</p><br/>
    <a href="/docs">📖 Documentação</a>
    <a href="/health">💚 Status</a>
    <a href="/historico">📊 Histórico</a>
    </body></html>
    """

@app.get("/health")
async def health():
    """Status do sistema."""
    stats = improver.estatisticas()
    ebooks = list(OUTPUT_DIR.glob("*/metadata.json"))
    return {
        "status": "online",
        "versao": "4.0.0",
        "modelo_ia": "Groq Mixtral 8x7B (Gratuito)",
        "timestamp": datetime.now().isoformat(),
        "total_ebooks_gerados": len(ebooks),
        "sistema_aprendizado": stats,
    }

@app.get("/trending")
async def trending():
    """Pesquisa temas trending agora."""
    try:
        resultado = await researcher.pesquisar_trending()
        return JSONResponse(content=resultado)
    except Exception as e:
        logger.exception("Erro ao pesquisar trending")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gerar-ebook")
async def gerar_ebook(request: GerarEbookRequest):
    """Gera um e-book completo (3-8 minutos)."""
    forcar_tema = None
    if request.tema_customizado:
        forcar_tema = {
            "tema_escolhido": request.tema_customizado,
            "subtitulo": f"O guia definitivo sobre {request.tema_customizado}",
            "nicho": request.nicho or "Desenvolvimento Pessoal",
            "preco_sugerido": "R$ 297",
            "publico_alvo": "Profissionais e empreendedores",
            "problema_resolvido": f"Como dominar {request.tema_customizado}",
            "potencial_vendas": "Alto",
            "justificativa": "Tema solicitado pelo usuário",
            "capitulos_sugeridos": [
                "Fundamentos", "Estratégia", "Execução",
                "Escala", "Resultados", "Casos de Sucesso", "Próximo Nível"
            ],
            "palavras_chave_seo": [request.tema_customizado or ""],
            "top5_alternativas": [],
        }

    try:
        resultado = await gerador.gerar_ebook_completo(forcar_tema=forcar_tema)
        ebook_id = resultado["ebook_id"]
        pdf = resultado["pdf"]
        meta = resultado["metadata"]
        avaliacao = resultado["avaliacao"]

        return Response(
            content=pdf if pdf != b"PDF_UNAVAILABLE" else b"",
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="ebook_{ebook_id}.pdf"',
                "X-Ebook-ID": ebook_id,
                "X-Score": str(avaliacao.get("score_total", 0)),
                "X-Tema": meta.get("tema", {}).get("tema_escolhido", "")[:50],
            },
        )
    except Exception as e:
        logger.exception("Erro ao gerar e-book")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{ebook_id}/pdf")
async def download_pdf(ebook_id: str):
    """Baixa o PDF."""
    pdf_path = OUTPUT_DIR / ebook_id / "ebook.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="E-book não encontrado")
    return FileResponse(path=str(pdf_path), media_type="application/pdf", filename=f"ebook_{ebook_id}.pdf")

@app.get("/download/{ebook_id}/html", response_class=HTMLResponse)
async def visualizar_html(ebook_id: str):
    """Visualiza HTML no navegador."""
    html_path = OUTPUT_DIR / ebook_id / "ebook.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="E-book não encontrado")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/ebook/{ebook_id}")
async def info_ebook(ebook_id: str):
    """Metadados do e-book."""
    meta_path = OUTPUT_DIR / ebook_id / "metadata.json"
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="E-book não encontrado")
    return JSONResponse(content=json.loads(meta_path.read_text(encoding="utf-8")))

@app.get("/historico")
async def historico():
    """Lista todos os e-books gerados."""
    ebooks = []
    for meta_file in sorted(OUTPUT_DIR.glob("*/metadata.json"), reverse=True):
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            ebooks.append({
                "ebook_id": meta.get("ebook_id"),
                "gerado_em": meta.get("gerado_em"),
                "tema": meta.get("tema", {}).get("tema_escolhido"),
                "score_final": meta.get("score_final"),
                "aprovado": meta.get("aprovado"),
                "links": {
                    "pdf": f"/download/{meta.get('ebook_id')}/pdf",
                    "html": f"/download/{meta.get('ebook_id')}/html",
                }
            })
        except Exception:
            continue

    stats = improver.estatisticas()
    return {"ebooks": ebooks, "estatisticas_sistema": stats}

@app.get("/aprendizado")
async def aprendizado():
    """Estado do sistema de auto-melhoria."""
    prompts = improver.carregar_prompts()
    historico = improver.carregar_historico()

    return {
        "versao_prompts": prompts.get("versao"),
        "total_geracoes": len(historico),
        "score_medio_historico": prompts.get("score_medio", 0),
        "insight_aprendido": prompts.get("insight_aprendido", "Aprendendo..."),
        "melhorias_acumuladas": prompts.get("melhorias_acumuladas", []),
        "evolucao_scores": [
            {"geracao": h.get("id"), "score": h.get("score_total"), "tema": h.get("tema")}
            for h in historico[-20:]
        ],
    }

if __name__ == "__main__":
    print("")
    print("=" * 70)
    print("  ✅ IA GERADORA DE E-BOOKS COM GROQ v4.0")
    print("=" * 70)
    print("")
    print("  🚀 Endpoints principais:")
    print("    POST /gerar-ebook  - Gera e-book completo (3-8 min)")
    print("    GET  /trending     - Pesquisa temas lucrativos agora")
    print("    GET  /historico    - Todos os e-books gerados")
    print("    GET  /aprendizado  - Estado do aprendizado de IA")
    print("    GET  /docs         - Documentação interativa")
    print("")
    print("  📌 Acesse: http://localhost:8000")
    print("=" * 70)
    print("")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        timeout_keep_alive=600,
    )
