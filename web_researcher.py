"""
web_researcher.py
Pesquisa na internet os temas de e-book mais lucrativos usando Serper API + Groq.
"""
import json
import logging
import asyncio
import httpx
from typing import List, Dict, Any
from config import SERPER_API_KEY
from groq_client import obter_cliente_groq

logger = logging.getLogger(__name__)


class WebResearcher:
    """Pesquisa tendências de e-books usando Serper + Groq."""
    
    QUERIES = [
        "best selling ebooks 2025 high income niches profitable",
        "ebooks mais vendidos amazon kindle 2025 nicho lucrativo",
        "luxury professional ebook topics high ticket sales",
        "kindle bestseller ebook ideas most profitable 2025",
        "digital products ebook passive income best niches 2025",
        "ebook millionaire topics wealth mindset business luxury",
    ]

    def __init__(self):
        self.serper_key = SERPER_API_KEY
        self.groq = obter_cliente_groq()

    async def _serper_search(self, query: str, num: int = 8) -> List[Dict]:
        """Busca no Google via Serper."""
        if not self.serper_key:
            logger.warning("⚠️  SERPER_API_KEY não definida - usando dados mock")
            return self._mock_resultados()

        headers = {
            "X-API-KEY": self.serper_key,
            "Content-Type": "application/json",
        }
        payload = {"q": query, "num": num, "gl": "br", "hl": "pt"}

        try:
            async with httpx.AsyncClient(timeout=15.0) as http:
                resp = await http.post(
                    "https://google.serper.dev/search",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"✅ Serper: {len(data.get('organic', []))} resultados para '{query}'")
                return data.get("organic", [])
        except Exception as e:
            logger.error(f"❌ Erro Serper: {e}")
            return self._mock_resultados()

    def _mock_resultados(self) -> List[Dict]:
        """Retorna dados mock quando Serper não está disponível."""
        return [
            {
                "title": "Como ganhar dinheiro com e-books em 2025",
                "snippet": "Guia completo sobre monetização digital"
            },
            {
                "title": "Nicho mais lucrativo: Investimentos financeiros",
                "snippet": "E-books sobre finanças pessoais vendem bem"
            },
            {
                "title": "Marketing digital premium",
                "snippet": "Curso e-book de high ticket"
            },
        ]

    async def pesquisar_trending(self) -> Dict[str, Any]:
        """
        Pesquisa o que está em alta no mercado de e-books.
        Retorna o melhor tema para gerar agora.
        """
        logger.info("🔍 Pesquisando tendências de e-books...")

        # Executa buscas em paralelo
        tasks = [self._serper_search(q) for q in self.QUERIES]
        resultados_brutos = await asyncio.gather(*tasks, return_exceptions=True)

        # Coleta snippets
        todos_snippets: List[str] = []
        for r in resultados_brutos:
            if isinstance(r, Exception):
                logger.warning(f"Falha em busca: {r}")
                continue
            for item in r:
                titulo = item.get("title", "")
                snippet = item.get("snippet", "")
                if titulo or snippet:
                    todos_snippets.append(f"- {titulo}: {snippet}")

        texto_pesquisa = "\n".join(todos_snippets[:40])
        logger.info(f"📊 {len(todos_snippets)} resultados coletados da pesquisa web")

        # Groq escolhe melhor tema
        prompt = f"""
Você é um especialista em marketing digital e mercado editorial digital.
Analise estes dados reais coletados hoje da internet sobre e-books lucrativos:

{texto_pesquisa}

Com base nessa análise de mercado REAL, escolha o MELHOR tema para criar um e-book:
- Que seja PROFISSIONAL e de LUXO (público: executivos, empreendedores, investidores)
- Que tenha ALTÍSSIMO potencial de vendas (ticket: R$ 97 a R$ 997)
- Que resolva um problema URGENTE de pessoas com alto poder aquisitivo
- Que seja ÚNICO e diferenciado, não genérico
- Que esteja em ALTA DEMANDA agora em 2025

Retorne APENAS JSON válido:
{{
  "tema_escolhido": "Título exato do e-book",
  "subtitulo": "Subtítulo que vende em até 15 palavras",
  "nicho": "Nicho de mercado específico",
  "preco_sugerido": "R$ 297",
  "publico_alvo": "Descrição detalhada de quem vai comprar",
  "problema_resolvido": "Dor principal que este e-book resolve",
  "potencial_vendas": "Alto",
  "justificativa": "Por que este tema vai gerar muita renda agora",
  "capitulos_sugeridos": ["Cap 1", "Cap 2", "Cap 3", "Cap 4", "Cap 5", "Cap 6", "Cap 7"],
  "palavras_chave_seo": ["kw1", "kw2", "kw3"],
  "top5_alternativas": [
    {{"tema": "alternativa 1", "potencial": "Alto"}},
    {{"tema": "alternativa 2", "potencial": "Alto"}}
  ]
}}
"""

        try:
            resultado = await self.groq.completar_json(prompt, temperatura=0.3)
            logger.info(f"🎯 Tema escolhido: {resultado.get('tema_escolhido')}")
            return resultado
        except Exception as e:
            logger.error(f"❌ Erro ao escolher tema: {e}")
            # Retorna tema fallback
            return {
                "tema_escolhido": "Marketing Digital de Alta Performance",
                "subtitulo": "O guia definitivo para escalar suas vendas online",
                "nicho": "Marketing Digital",
                "preco_sugerido": "R$ 297",
                "publico_alvo": "Empreendedores e profissionais de marketing",
                "problema_resolvido": "Como gerar leads qualificados e aumentar conversão",
                "potencial_vendas": "Muito Alto",
                "justificativa": "Mercado de marketing digital está em alta demanda",
                "capitulos_sugeridos": [
                    "Fundamentos do Marketing Digital",
                    "Estratégia de Conteúdo",
                    "Tráfego Pago",
                    "Email Marketing",
                    "Vendas e Conversão",
                    "Automação",
                    "Escala e Multiplicação"
                ],
                "palavras_chave_seo": ["marketing digital", "vendas online", "leads"],
                "top5_alternativas": [],
            }
