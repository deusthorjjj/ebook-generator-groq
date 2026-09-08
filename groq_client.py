"""
groq_client.py
Cliente wrapper para Groq API com retry logic e error handling robusto.
"""
import json
import logging
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from config import GROQ_CONFIG, MAX_RETRY_ATTEMPTS, TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


class GroqClient:
    """Cliente para Groq API com tratamento robusto de erros."""
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
        self.timeout = TIMEOUT_SECONDS
        self.max_retries = MAX_RETRY_ATTEMPTS
    
    async def _fazer_request(
        self,
        mensagens: List[Dict[str, str]],
        temperatura: float = 0.3,
        max_tokens: int = 2000,
        response_format: Optional[Dict] = None,
        tentativa: int = 1,
    ) -> str:
        """
        Faz request para Groq API com retry automático.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": mensagens,
            "temperature": temperatura,
            "max_tokens": max_tokens,
        }
        
        # Se solicitar JSON, adiciona format constraint
        if response_format and response_format.get("type") == "json_object":
            payload["response_format"] = {"type": "json_object"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"[Tentativa {tentativa}] Enviando para Groq: {len(json.dumps(payload))} bytes")
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                
                # Validar status code
                if response.status_code == 429:  # Rate limit
                    if tentativa < self.max_retries:
                        espera = 2 ** tentativa  # Exponential backoff
                        logger.warning(f"Rate limit atingido. Aguardando {espera}s...")
                        await asyncio.sleep(espera)
                        return await self._fazer_request(
                            mensagens, temperatura, max_tokens, response_format, tentativa + 1
                        )
                    else:
                        raise RuntimeError("Rate limit - max retries atingido")
                
                elif response.status_code == 401:
                    raise RuntimeError("❌ GROQ_API_KEY inválida ou expirada")
                
                elif response.status_code >= 500:
                    if tentativa < self.max_retries:
                        espera = 2 ** tentativa
                        logger.warning(f"Erro servidor ({response.status_code}). Retry em {espera}s...")
                        await asyncio.sleep(espera)
                        return await self._fazer_request(
                            mensagens, temperatura, max_tokens, response_format, tentativa + 1
                        )
                    else:
                        raise RuntimeError(f"Erro servidor persistente: {response.status_code}")
                
                elif response.status_code != 200:
                    try:
                        erro = response.json()
                        msg_erro = erro.get("error", {}).get("message", str(erro))
                    except:
                        msg_erro = response.text
                    raise RuntimeError(f"Erro Groq ({response.status_code}): {msg_erro}")
                
                # Sucesso
                data = response.json()
                conteudo = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not conteudo:
                    raise RuntimeError("Resposta vazia da Groq")
                
                logger.info(f"✅ Groq respondeu com sucesso ({len(conteudo)} chars)")
                return conteudo
                
        except httpx.TimeoutException:
            if tentativa < self.max_retries:
                espera = 2 ** tentativa
                logger.warning(f"Timeout ({self.timeout}s). Retry em {espera}s...")
                await asyncio.sleep(espera)
                return await self._fazer_request(
                    mensagens, temperatura, max_tokens, response_format, tentativa + 1
                )
            else:
                raise RuntimeError(f"Timeout persistente após {self.max_retries} tentativas")
        
        except Exception as e:
            logger.error(f"Erro inesperado na request Groq: {e}")
            raise
    
    async def completar(
        self,
        prompt: str,
        temperatura: float = 0.3,
        max_tokens: int = 1000,
    ) -> str:
        """Completa um prompt simples."""
        return await self._fazer_request(
            [{"role": "user", "content": prompt}],
            temperatura=temperatura,
            max_tokens=max_tokens,
        )
    
    async def completar_json(
        self,
        prompt: str,
        temperatura: float = 0.3,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """Completa um prompt e retorna JSON parseado."""
        conteudo = await self._fazer_request(
            [{"role": "user", "content": prompt}],
            temperatura=temperatura,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        
        try:
            # Tenta remover markdown code blocks se existirem
            if "```json" in conteudo:
                conteudo = conteudo.split("```json")[1].split("```")[0].strip()
            elif "```" in conteudo:
                conteudo = conteudo.split("```")[1].split("```")[0].strip()
            
            return json.loads(conteudo)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da Groq: {e}\nConteudo: {conteudo[:200]}")
            raise RuntimeError(f"Groq retornou JSON inválido: {e}")


# Cliente global
_groq_client: Optional[GroqClient] = None


def obter_cliente_groq() -> GroqClient:
    """Retorna instância global do cliente Groq (singleton)."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient(
            api_key=GROQ_CONFIG["api_key"],
            model=GROQ_CONFIG["model"],
        )
    return _groq_client
