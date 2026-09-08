"""
self_improver.py
Sistema de auto-avaliação e melhoria contínua focado em maximizar receita.
Aprende com cada geração para gerar e-books cada vez mais lucrativos.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from groq_client import obter_cliente_groq

logger = logging.getLogger(__name__)

HISTORY_FILE = Path("prompts/history.json")
PROMPTS_FILE = Path("prompts/system_prompts.json")

PROMPTS_INICIAIS = {
    "versao": "1.0",
    "criado_em": datetime.now().isoformat(),
    "geracoes": 0,
    "score_medio": 0.0,
    "instrucoes_escritor": (
        "Escreva conteúdo ALTAMENTE PROFISSIONAL para cada capítulo. "
        "Use dados reais, exemplos concretos, estudos de caso, checklists e insights exclusivos. "
        "O leitor deve sentir que pagou pouco pelo valor recebido. "
        "Tom: sofisticado, direto, autoritário. Mínimo de 700 palavras por seção."
    ),
    "instrucoes_design": (
        "Design LUXUOSO com fundo escuro (#0a0a0a), acento dourado (#d4af37). "
        "Tipografia: Playfair Display para títulos, Inter para corpo. "
        "Muito espaço em branco. Gráfico de dados obrigatório por capítulo. "
        "Imagens full-width com legenda profissional."
    ),
    "instrucoes_monetizacao": (
        "Cada capítulo deve conter: 1 insight exclusivo, 1 framework acionável, "
        "1 checklist prático. O e-book deve justificar preço premium de R$ 297+. "
        "Inclua resultados mensuráveis e transformação de vida do leitor."
    ),
    "melhorias_acumuladas": [],
}


class SelfImprover:
    """Sistema de auto-melhoria baseado em scores e histórico."""
    
    def __init__(self):
        self.groq = obter_cliente_groq()
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        PROMPTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._garantir_arquivos()

    def _garantir_arquivos(self):
        """Cria arquivos de configuração se não existirem."""
        if not PROMPTS_FILE.exists():
            PROMPTS_FILE.write_text(
                json.dumps(PROMPTS_INICIAIS, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info("📝 Criado arquivo de prompts inicial")
        
        if not HISTORY_FILE.exists():
            HISTORY_FILE.write_text("[]", encoding="utf-8")
            logger.info("📝 Criado arquivo de histórico inicial")

    def carregar_prompts(self) -> Dict[str, Any]:
        """Carrega prompts do sistema."""
        return json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))

    def carregar_historico(self) -> List[Dict]:
        """Carrega histórico de gerações."""
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []

    async def avaliar_ebook(
        self,
        tema: Dict[str, Any],
        html: str,
        capitulos: List[Dict],
    ) -> Dict[str, Any]:
        """
        Groq avalia o e-book em 6 critérios focados em monetização.
        Retorna scores detalhados e sugestões de melhoria.
        """
        sumario_capitulos = "\n".join(
            f"- {c.get('titulo', '')}: {c.get('resumo', '')[:200]}"
            for c in capitulos
        )

        prompt = f"""
Você é um editor senior especialista em e-books de alto valor e marketing digital.
Avalie este e-book com critério RIGOROSO focado em POTENCIAL DE RECEITA.

TEMA: {tema.get('tema_escolhido')}
SUBTITULO: {tema.get('subtitulo')}
PREÇO SUGERIDO: {tema.get('preco_sugerido')}
PÚBLICO: {tema.get('publico_alvo')}

CAPÍTULOS GERADOS:
{sumario_capitulos}

TAMANHO DO HTML: {len(html):,} caracteres

Avalie cada critério de 0 a 10 e justifique:

1. QUALIDADE DO CONTEÚDO (0-10): Profundidade, unicidade, dados concretos, exemplos reais
2. DESIGN E VISUAL (0-10): Profissionalismo, luxo, layout, tipografia, imagens
3. POTENCIAL DE VENDA (0-10): O leitor pagaria R$ 297+ por isso?
4. VALOR PERCEBIDO (0-10): O leitor sente que recebeu mais do que pagou
5. DIFERENCIAÇÃO (0-10): Quanto este e-book se destaca da concorrência
6. TRANSFORMAÇÃO (0-10): Clareza do resultado que o leitor vai obter

Retorne APENAS JSON válido:
{{
  "scores": {{
    "qualidade_conteudo": 0,
    "design_visual": 0,
    "potencial_venda": 0,
    "valor_percebido": 0,
    "diferenciacao": 0,
    "transformacao": 0
  }},
  "score_total": 0.0,
  "score_monetizacao": 0.0,
  "aprovado": false,
  "pontos_fortes": ["ponto1", "ponto2"],
  "pontos_fracos": ["fraco1", "fraco2"],
  "melhorias_urgentes": ["melhoria1", "melhoria2"],
  "feedback_design": "feedback específico",
  "feedback_conteudo": "feedback específico",
  "justificativa_preco": "Porque..."
}}
"""

        try:
            avaliacao = await self.groq.completar_json(prompt, temperatura=0.2, max_tokens=1500)
            
            scores = avaliacao.get("scores", {})
            total = sum(scores.values()) / max(len(scores), 1)
            avaliacao["score_total"] = round(total, 2)
            avaliacao["aprovado"] = total >= 7.5

            logger.info(
                f"📊 Avaliação: {total:.1f}/10 | "
                f"Aprovado: {avaliacao['aprovado']} | "
                f"Venda: {scores.get('potencial_venda', 0)}/10"
            )
            return avaliacao
        except Exception as e:
            logger.error(f"❌ Erro ao avaliar e-book: {e}")
            # Retorna avaliação conservadora em caso de erro
            return {
                "scores": {"qualidade_conteudo": 6, "design_visual": 6, "potencial_venda": 6,
                          "valor_percebido": 6, "diferenciacao": 5, "transformacao": 6},
                "score_total": 5.83,
                "score_monetizacao": 5.5,
                "aprovado": False,
                "pontos_fortes": ["Estrutura básica ok"],
                "pontos_fracos": ["Precisa de melhoria"],
                "melhorias_urgentes": ["Aprofundar conteúdo"],
                "feedback_design": "Design ok",
                "feedback_conteudo": "Conteúdo básico",
                "justificativa_preco": "Preço justo para o conteúdo oferecido"
            }

    async def gerar_instrucoes_melhoria(
        self,
        avaliacao: Dict[str, Any],
        prompts_atuais: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Gera instruções para melhorar a geração."""
        prompt = f"""
Um e-book foi avaliado com score {avaliacao.get('score_total', 0):.1f}/10.

PONTOS FRACOS: {avaliacao.get('pontos_fracos', [])}
MELHORIAS URGENTES: {avaliacao.get('melhorias_urgentes', [])}
FEEDBACK DESIGN: {avaliacao.get('feedback_design', '')}
FEEDBACK CONTEÚDO: {avaliacao.get('feedback_conteudo', '')}

Gere instruções ESPECÍFICAS e ACIONÁVEIS. Retorne APENAS JSON:
{{
  "reescrever_secoes": ["lista"],
  "instrucao_escritor_atualizada": "instrução completa melhorada",
  "instrucao_design_atualizada": "instrução de design melhorada",
  "focar_em": ["aspecto1", "aspecto2"],
  "evitar": ["problema1", "problema2"]
}}
"""
        try:
            return await self.groq.completar_json(prompt, temperatura=0.3, max_tokens=1200)
        except Exception as e:
            logger.error(f"❌ Erro ao gerar instruções de melhoria: {e}")
            return {
                "reescrever_secoes": ["todas"],
                "instrucao_escritor_atualizada": prompts_atuais.get("instrucoes_escritor", ""),
                "instrucao_design_atualizada": prompts_atuais.get("instrucoes_design", ""),
                "focar_em": ["qualidade", "profundidade"],
                "evitar": ["genérico", "raso"]
            }

    async def aprender_e_evoluir(
        self,
        tema: Dict[str, Any],
        avaliacao: Dict[str, Any],
        prompts_usados: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analisa histórico e evolui prompts para melhorar próximas gerações."""
        historico = self.carregar_historico()

        # Salva esta geração
        entrada = {
            "id": len(historico) + 1,
            "timestamp": datetime.now().isoformat(),
            "tema": tema.get("tema_escolhido"),
            "nicho": tema.get("nicho"),
            "preco_sugerido": tema.get("preco_sugerido"),
            "score_total": avaliacao.get("score_total"),
            "score_monetizacao": avaliacao.get("score_monetizacao"),
            "scores_detalhe": avaliacao.get("scores", {}),
            "pontos_fortes": avaliacao.get("pontos_fortes", []),
            "pontos_fracos": avaliacao.get("pontos_fracos", []),
            "prompts_versao": prompts_usados.get("versao", "1.0"),
        }
        historico.append(entrada)
        HISTORY_FILE.write_text(
            json.dumps(historico, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Só evolui com 3+ gerações
        if len(historico) < 3:
            logger.info(f"⏳ Histórico com {len(historico)} geração(ões). Precisam de 3 para evoluir prompts.")
            return prompts_usados

        logger.info("🧠 Analisando histórico para evolução de prompts...")
        
        # Analisa padrões
        historico_ordenado = sorted(historico, key=lambda x: x.get("score_total", 0), reverse=True)
        melhores = historico_ordenado[:3]

        resumo_melhores = json.dumps(
            [{k: v for k, v in h.items() if k != "id"} for h in melhores],
            indent=2, ensure_ascii=False,
        )

        prompt_evolucao = f"""
Você é um especialista em otimização de sistemas de IA para geração de conteúdo.

HISTÓRICO DE GERAÇÕES (total: {len(historico)}):
Score médio: {sum(h.get('score_total', 0) for h in historico) / len(historico):.2f}/10

MELHORES GERAÇÕES:
{resumo_melhores}

Com base nos padrões, EVOLUA as instruções para gerar e-books ainda mais lucrativos.

Retorne APENAS JSON:
{{
  "versao": "nova_versao",
  "instrucoes_escritor": "instrução melhorada e específica",
  "instrucoes_design": "instrução de design melhorada",
  "instrucoes_monetizacao": "instrução de monetização melhorada",
  "melhorias_acumuladas": ["melhoria1", "melhoria2"],
  "insight_aprendido": "O que o sistema aprendeu"
}}
"""

        try:
            novos_prompts = await self.groq.completar_json(prompt_evolucao, temperatura=0.3, max_tokens=1500)
            novos_prompts["geracoes"] = len(historico)
            novos_prompts["score_medio"] = round(
                sum(h.get("score_total", 0) for h in historico) / len(historico), 2
            )
            novos_prompts["atualizado_em"] = datetime.now().isoformat()

            PROMPTS_FILE.write_text(
                json.dumps(novos_prompts, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            logger.info(f"🎓 Prompts evoluidos! Score médio: {novos_prompts['score_medio']}/10")
            return novos_prompts
        except Exception as e:
            logger.error(f"❌ Erro ao evoluir prompts: {e}")
            return prompts_usados

    def estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema."""
        historico = self.carregar_historico()
        prompts = self.carregar_prompts()
        
        if not historico:
            return {
                "total_geracoes": 0,
                "mensagem": "Nenhuma geração ainda",
                "versao_prompts": prompts.get("versao", "1.0")
            }

        scores = [h.get("score_total", 0) for h in historico]
        return {
            "total_geracoes": len(historico),
            "score_medio": round(sum(scores) / len(scores), 2),
            "score_maximo": max(scores),
            "score_minimo": min(scores),
            "versao_prompts": prompts.get("versao", "1.0"),
            "insight_mais_recente": prompts.get("insight_aprendido", "Sistema iniciado"),
            "melhorias_acumuladas": len(prompts.get("melhorias_acumuladas", [])),
            "ultima_geracao": historico[-1].get("timestamp", "N/A"),
        }
