"""
image_service.py
Busca imagens de alta qualidade no Pexels (gratuito) e retorna como base64.
Fallback para SVG placeholder quando API não está disponível.
"""
import os
import base64
import asyncio
import logging
from typing import Optional, List
import httpx

logger = logging.getLogger(__name__)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

PLACEHOLDER_SVG = """<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080' viewBox='0 0 1920 1080'>
  <defs>
    <linearGradient id='g' x1='0%' y1='0%' x2='100%' y2='100%'>
      <stop offset='0%' stop-color='#0a0a0a'/>
      <stop offset='100%' stop-color='#1a1a2e'/>
    </linearGradient>
  </defs>
  <rect width='1920' height='1080' fill='url(#g)'/>
  <text x='960' y='540' fill='#d4af37' font-size='48' text-anchor='middle' font-family='serif' font-weight='bold'>
    EBOOK PROFISSIONAL
  </text>
</svg>"""


class ImageService:
    """Serviço para buscar imagens de alta qualidade com fallback robusto."""
    
    def __init__(self):
        self.pexels_key = PEXELS_API_KEY
        self._cache: dict = {}

    def _placeholder(self) -> str:
        """Retorna placeholder SVG como data URI."""
        svg_b64 = base64.b64encode(PLACEHOLDER_SVG.encode()).decode()
        return f"data:image/svg+xml;base64,{svg_b64}"

    async def buscar_imagem(
        self,
        query: str,
        orientacao: str = "landscape",
        tamanho: str = "large",
    ) -> str:
        """
        Busca imagem no Pexels e retorna como data URI base64.
        Fallback para SVG placeholder se Pexels não estiver configurado.
        """
        cache_key = f"{query}_{orientacao}"
        if cache_key in self._cache:
            logger.debug(f"📸 Imagem em cache: {query}")
            return self._cache[cache_key]

        if not self.pexels_key:
            logger.warning(f"⚠️  PEXELS_API_KEY não definida - usando placeholder para '{query}'")
            return self._placeholder()

        headers = {"Authorization": self.pexels_key}
        params = {
            "query": query,
            "orientation": orientacao,
            "size": tamanho,
            "per_page": 5,
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as http:
                resp = await http.get(
                    "https://api.pexels.com/v1/search",
                    headers=headers,
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()

                fotos = data.get("photos", [])
                if not fotos:
                    logger.warning(f"📸 Nenhuma foto encontrada para: {query}")
                    return self._placeholder()

                # Escolhe foto com melhor resolução
                foto = max(fotos, key=lambda f: f.get("width", 0) * f.get("height", 0))
                url = foto["src"].get("original") or foto["src"].get("large2x") or foto["src"]["large"]

                img_resp = await http.get(url, timeout=40.0, follow_redirects=True)
                img_resp.raise_for_status()

                content_type = img_resp.headers.get("content-type", "image/jpeg").split(";")[0]
                img_b64 = base64.b64encode(img_resp.content).decode()
                data_uri = f"data:{content_type};base64,{img_b64}"

                self._cache[cache_key] = data_uri
                tamanho_kb = len(img_resp.content) // 1024
                logger.info(f"✅ Imagem obtida: {query} ({tamanho_kb}KB)")
                return data_uri

        except httpx.TimeoutException:
            logger.warning(f"⏱️  Timeout ao buscar imagem '{query}'")
            return self._placeholder()
        except Exception as e:
            logger.error(f"❌ Erro ao buscar imagem '{query}': {e}")
            return self._placeholder()

    async def buscar_multiplas(self, queries: List[str]) -> List[str]:
        """Busca múltiplas imagens em paralelo."""
        tasks = [self.buscar_imagem(q) for q in queries]
        return await asyncio.gather(*tasks)

    async def buscar_capa(self, tema: str, nicho: str) -> str:
        """Busca imagem de capa específica para o tema do e-book."""
        queries_tentativa = [
            f"{tema} luxury professional",
            f"{nicho} executive business luxury",
            f"luxury business wealth success",
        ]
        for q in queries_tentativa:
            uri = await self.buscar_imagem(q, orientacao="landscape", tamanho="large")
            if not uri.startswith("data:image/svg+xml"):
                logger.info(f"🎨 Capa encontrada: {q}")
                return uri
        
        logger.warning("🎨 Usando capa placeholder")
        return self._placeholder()
