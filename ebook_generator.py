"""
ebook_generator.py
Orquestra todo o pipeline de geração do e-book com auto-melhoria usando Groq.
"""
import os
import json
import uuid
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import OUTPUT_DIR, MAX_TENTATIVAS_MELHORIA, MIN_SCORE_APROVACAO
from web_researcher import WebResearcher
from image_service import ImageService
from self_improver import SelfImprover
from html_template import montar_html_ebook
from groq_client import obter_cliente_groq

logger = logging.getLogger(__name__)


class EbookGenerator:
    """Gerador completo de e-books com auto-melhoria."""
    
    def __init__(self):
        self.groq = obter_cliente_groq()
        self.researcher = WebResearcher()
        self.images = ImageService()
        self.improver = SelfImprover()
        logger.info("🚀 EbookGenerator inicializado")

    async def _gerar_estrutura(
        self, tema: Dict[str, Any], prompts: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Gera o outline completo do e-book com capítulos detalhados."""
        capitulos_sugeridos = tema.get("capitulos_sugeridos", [])
        logger.info(f"📚 Gerando estrutura com {len(capitulos_sugeridos)} capítulos...")

        prompt = f"""
Você é um expert em estruturação de e-books profissionais de luxo.
Crie a estrutura COMPLETA de um e-book:

TEMA: {tema.get('tema_escolhido')}
SUBTÍTULO: {tema.get('subtitulo')}
PÚBLICO: {tema.get('publico_alvo')}
PROBLEMA: {tema.get('problema_resolvido')}
PREÇO: {tema.get('preco_sugerido')}
CAPÍTULOS SUGERIDOS: {json.dumps(capitulos_sugeridos)}

Para cada capítulo, defina:
- título: Título atrativo e específico
- resumo: Descrição do que o leitor vai aprender (2-3 frases)
- tópicos: Lista de 4-6 tópicos abordados
- insights: Lista de 3 insights exclusivos
- checklist: Lista de 4-5 ações que o leitor deve tomar
- query_imagem: Busca em inglês para imagem de alta qualidade
- tipo_grafico: "bar" | "line" | "doughnut" | "radar"
- dados_grafico_descricao: O que o gráfico vai mostrar

Retorne APENAS JSON válido:
{{
  "capitulos": [
    {{
      "titulo": "...",
      "resumo": "...",
      "topicos": ["..."],
      "insights": ["..."],
      "checklist": ["..."],
      "query_imagem": "...",
      "tipo_grafico": "bar",
      "dados_grafico_descricao": "..."
    }}
  ]
}}
"""
        data = await self.groq.completar_json(prompt, temperatura=0.3)
        return data.get("capitulos", [])

    async def _escrever_capitulo(
        self,
        cap: Dict[str, Any],
        tema: Dict[str, Any],
        prompts: Dict[str, Any],
    ) -> str:
        """Escreve o conteúdo completo de um capítulo."""
        melhorias = "\n".join(prompts.get("melhorias_acumuladas", []))
        instrucao_extra = f"MELHORIAS JÁ APRENDIDAS:\n{melhorias}" if melhorias else ""

        prompt = f"""
{prompts.get('instrucoes_escritor', '')}
{instrucao_extra}

Escreva o conteúdo COMPLETO e DETALHADO do capítulo:

LIVRO: {tema.get('tema_escolhido')}
CAPÍTULO: {cap.get('titulo')}
RESUMO: {cap.get('resumo')}
TÓPICOS A COBRIR: {json.dumps(cap.get('topicos', []))}
PÚBLICO: {tema.get('publico_alvo')}
PROBLEMA QUE RESOLVE: {tema.get('problema_resolvido')}

REGRAS:
- Mínimo 600 palavras de conteúdo rico e exclusivo
- Parágrafos bem espaçados
- Inclua dados, estatísticas, estudos de caso e exemplos reais
- Tom: sofisticado, autoritário, mas acessível
- Não use markdown

Escreva apenas o texto do conteúdo:
"""
        conteudo = await self.groq.completar(prompt, temperatura=0.4, max_tokens=1500)
        return conteudo or "Conteúdo gerado."

    async def _escrever_todos_capitulos(
        self,
        capitulos: List[Dict],
        tema: Dict,
        prompts: Dict,
    ) -> List[Dict]:
        """Escreve todos os capítulos em paralelo."""
        logger.info(f"✍️  Escrevendo {len(capitulos)} capítulos em paralelo...")
        tasks = [self._escrever_capitulo(cap, tema, prompts) for cap in capitulos]
        conteudos = await asyncio.gather(*tasks)
        for cap, conteudo in zip(capitulos, conteudos):
            cap["conteudo"] = conteudo
        return capitulos

    async def _gerar_dados_grafico(
        self, cap: Dict[str, Any], tema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera dados realistas para o gráfico do capítulo."""
        prompt = f"""
Gere dados REAIS e RELEVANTES para um gráfico Chart.js sobre:

CAPÍTULO: {cap.get('titulo')}
DESCRIÇÃO: {cap.get('dados_grafico_descricao', '')}
TEMA: {tema.get('tema_escolhido')}
TIPO: {cap.get('tipo_grafico', 'bar')}

Retorne APENAS JSON válido compatível com Chart.js:
{{
  "tipo": "bar",
  "titulo": "Título do gráfico",
  "data": {{
    "labels": ["Label1", "Label2", "Label3", "Label4", "Label5"],
    "datasets": [{{
      "label": "Legenda",
      "data": [10, 20, 30, 40, 50],
      "backgroundColor": ["rgba(212,175,55,0.7)","rgba(192,155,35,0.7)","rgba(172,135,15,0.7)","rgba(152,115,5,0.7)","rgba(132,95,0,0.7)"],
      "borderColor": "rgba(212,175,55,1)",
      "borderWidth": 2
    }}]
  }}
}}
"""
        return await self.groq.completar_json(prompt, temperatura=0.3)

    async def _gerar_todos_graficos(
        self, capitulos: List[Dict], tema: Dict
    ) -> List[Dict]:
        """Gera gráficos para todos os capítulos em paralelo."""
        logger.info("📊 Gerando gráficos para todos os capítulos...")
        tasks = [self._gerar_dados_grafico(cap, tema) for cap in capitulos]
        return await asyncio.gather(*tasks)

    async def _renderizar_pdf(self, html: str) -> bytes:
        """Renderiza HTML para PDF via Playwright."""
        from playwright.async_api import async_playwright

        logger.info("🖨️  Renderizando PDF via Playwright...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                    ],
                )
                page = await browser.new_page(
                    viewport={"width": 1280, "height": 1800},
                    locale="pt-BR",
                )
                await page.set_content(html, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(2000)

                pdf = await page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "20mm", "bottom": "20mm", "left": "18mm", "right": "18mm"},
                    prefer_css_page_size=False,
                    scale=0.85,
                )
                await browser.close()

            tamanho_mb = len(pdf) / (1024 * 1024)
            logger.info(f"✅ PDF gerado: {tamanho_mb:.2f}MB")
            return pdf

        except Exception as e:
            logger.error(f"❌ Erro ao renderizar PDF: {e}")
            raise RuntimeError(f"Falha ao gerar PDF: {e}")

    async def gerar_ebook_completo(
        self, forcar_tema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Executa o pipeline completo de geração do e-book."""
        ebook_id = uuid.uuid4().hex[:12]
        logger.info(f"\n" + "="*70)
        logger.info(f"🎯 INICIANDO GERAÇÃO #{ebook_id}")
        logger.info(f"="*70 + "\n")

        # PESQUISA TRENDING
        if forcar_tema:
            tema = forcar_tema
            logger.info(f"✅ Tema forcado: {tema.get('tema_escolhido')}")
        else:
            tema = await self.researcher.pesquisar_trending()

        # CARREGA PROMPTS
        prompts = self.improver.carregar_prompts()
        logger.info(f"📝 Usando prompts versão: {prompts.get('versao', '1.0')}")

        html = ""
        pdf = b""
        avaliacao: Dict = {}
        capitulos: List[Dict] = []

        for tentativa in range(1, MAX_TENTATIVAS_MELHORIA + 1):
            logger.info(f"\n--- Tentativa {tentativa}/{MAX_TENTATIVAS_MELHORIA} ---")

            # ESTRUTURA
            capitulos = await self._gerar_estrutura(tema, prompts)
            logger.info(f"✅ {len(capitulos)} capítulos estruturados")

            # CONTEÚDO + IMAGENS + GRÁFICOS (em paralelo)
            conteudo_task = self._escrever_todos_capitulos(capitulos, tema, prompts)
            imagem_capa_task = self.images.buscar_capa(
                tema.get("tema_escolhido", ""), tema.get("nicho", "")
            )
            queries_imgs = [cap.get("query_imagem", tema.get("nicho", "luxury")) for cap in capitulos]
            imgs_caps_task = self.images.buscar_multiplas(queries_imgs)
            graficos_task = self._gerar_todos_graficos(capitulos, tema)

            capitulos, imagem_capa, imagens_caps, graficos = await asyncio.gather(
                conteudo_task, imagem_capa_task, imgs_caps_task, graficos_task
            )

            # MONTA HTML
            html = montar_html_ebook(
                tema=tema,
                capitulos=capitulos,
                imagem_capa=imagem_capa,
                imagens_capitulos=list(imagens_caps),
                graficos_data=list(graficos),
                prompts_versao=prompts.get("versao", "1.0"),
            )

            # RENDERIZA PDF
            try:
                pdf = await self._renderizar_pdf(html)
            except Exception as e:
                logger.warning(f"⚠️  Não foi possível renderizar PDF: {e}")
                pdf = b"PDF_UNAVAILABLE"

            # AUTO-AVALIAÇÃO
            avaliacao = await self.improver.avaliar_ebook(tema, html, capitulos)
            score = avaliacao.get("score_total", 0)

            logger.info(f"📊 Score tentativa {tentativa}: {score:.1f}/10")

            if avaliacao.get("aprovado", False):
                logger.info(f"✅ E-book APROVADO com score {score:.1f}/10!")
                break

            if tentativa < MAX_TENTATIVAS_MELHORIA:
                logger.info(f"⚠️  Score insuficiente ({score:.1f}). Gerando instruções de melhoria...")
                instrucoes = await self.improver.gerar_instrucoes_melhoria(avaliacao, prompts)
                if instrucoes.get("instrucao_escritor_atualizada"):
                    prompts["instrucoes_escritor"] = instrucoes["instrucao_escritor_atualizada"]
                if instrucoes.get("instrucao_design_atualizada"):
                    prompts["instrucoes_design"] = instrucoes["instrucao_design_atualizada"]

        # SALVA ARQUIVOS
        ebook_dir = OUTPUT_DIR / ebook_id
        ebook_dir.mkdir(exist_ok=True)

        html_path = ebook_dir / "ebook.html"
        pdf_path = ebook_dir / "ebook.pdf"
        meta_path = ebook_dir / "metadata.json"

        html_path.write_text(html, encoding="utf-8")
        if pdf != b"PDF_UNAVAILABLE":
            pdf_path.write_bytes(pdf)

        metadata = {
            "ebook_id": ebook_id,
            "gerado_em": datetime.now().isoformat(),
            "tema": tema,
            "score_final": avaliacao.get("score_total", 0),
            "scores_detalhe": avaliacao.get("scores", {}),
            "pontos_fortes": avaliacao.get("pontos_fortes", []),
            "aprovado": avaliacao.get("aprovado", False),
            "html_path": str(html_path),
            "pdf_path": str(pdf_path) if pdf != b"PDF_UNAVAILABLE" else "N/A",
            "tamanho_html_kb": len(html) // 1024,
            "tamanho_pdf_kb": len(pdf) // 1024 if pdf != b"PDF_UNAVAILABLE" else 0,
        }
        meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

        # APRENDE E EVOLUI
        prompts_originais = self.improver.carregar_prompts()
        await self.improver.aprender_e_evoluir(tema, avaliacao, prompts_originais)

        logger.info(f"\n" + "="*70)
        logger.info(f"✅ E-BOOK #{ebook_id} CONCLUÍDO | Score: {avaliacao.get('score_total', 0):.1f}/10")
        logger.info(f"="*70 + "\n")

        return {
            "ebook_id": ebook_id,
            "metadata": metadata,
            "html": html,
            "pdf": pdf,
            "avaliacao": avaliacao,
        }
