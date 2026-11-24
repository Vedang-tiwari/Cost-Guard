import json
import logging
from typing import Any

from app.evaluation.quality_metrics import length_consistency, semantic_similarity

logger = logging.getLogger("costguard.evaluation.llm_judge")

JUDGE_SYSTEM_PROMPT = """You are an impartial, highly rigorous AI evaluation judge.
Your role is to score a candidate AI model response against a reference response.
Evaluate across 4 distinct dimensions on a scale from 1 to 5:
1. correctness (1-5): Factual accuracy and alignment with reference.
2. adherence (1-5): Adherence to constraints, instructions, and user intent.
3. completeness (1-5): Thoroughness without missing essential facts.
4. formatting (1-5): Formatting, structure, clarity, and tone.

Respond ONLY with valid JSON in this exact structure:
{
  "correctness": 5,
  "adherence": 5,
  "completeness": 5,
  "formatting": 5,
  "reasoning": "Brief justification of scores"
}"""


class LLMJudge:
    """Evaluates candidate model outputs against reference model outputs using LLM-as-a-judge or heuristic fallback."""

    def __init__(self, provider_factory: Any | None = None) -> None:
        self.provider_factory = provider_factory

    async def judge(
        self,
        candidate: str,
        reference: str,
        prompt: str = "",
        model: str = "gpt-4o",
    ) -> dict[str, Any]:
        """
        Scores candidate output against reference output.
        Returns a dict with overall_score (0.0 to 1.0), dimension scores, and reasoning.
        """
        # Attempt LLM-assisted judge if provider is configured
        if self.provider_factory:
            try:
                provider = self.provider_factory.get_provider_for_model(model)
                user_msg = (
                    f"Prompt: {prompt}\n\n"
                    f"Reference Response:\n{reference}\n\n"
                    f"Candidate Response:\n{candidate}\n\n"
                    "Evaluate candidate compared to reference:"
                )
                from app.schemas.request import ChatCompletionRequest, ChatMessage

                req = ChatCompletionRequest(
                    model=model,
                    messages=[
                        ChatMessage(role="system", content=JUDGE_SYSTEM_PROMPT),
                        ChatMessage(role="user", content=user_msg),
                    ],
                    temperature=0.0,
                    max_tokens=300,
                )
                resp = await provider.complete(req)
                content = resp.choices[0].message.content.strip()

                # Parse JSON output
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                parsed = json.loads(content)
                correctness = float(parsed.get("correctness", 4))
                adherence = float(parsed.get("adherence", 4))
                completeness = float(parsed.get("completeness", 4))
                formatting = float(parsed.get("formatting", 4))
                reasoning = parsed.get("reasoning", "LLM Judge evaluation.")

                composite = (correctness * 0.4 + adherence * 0.3 + completeness * 0.2 + formatting * 0.1) / 5.0
                return {
                    "score": round(max(0.0, min(1.0, composite)), 4),
                    "dimensions": {
                        "correctness": correctness,
                        "adherence": adherence,
                        "completeness": completeness,
                        "formatting": formatting,
                    },
                    "reasoning": reasoning,
                    "method": "llm_judge",
                }
            except Exception as e:
                logger.warning(f"LLM judge invocation failed, using heuristic judge: {e}")

        # Deterministic heuristic judge fallback
        return self._heuristic_judge(candidate, reference)

    def _heuristic_judge(self, candidate: str, reference: str) -> dict[str, Any]:
        """Calculates a deterministic composite score when LLM judge is unavailable."""
        sim = semantic_similarity(candidate, reference)
        length_score = length_consistency(candidate, reference)

        # Dimension estimates
        correctness = min(5.0, max(1.0, sim * 5.0))
        adherence = min(5.0, max(1.0, (sim * 0.7 + length_score * 0.3) * 5.0))
        completeness = min(5.0, max(1.0, (length_score * 0.6 + sim * 0.4) * 5.0))
        formatting = 5.0 if ("```" in candidate and "```" in reference) or ("\n" in candidate and "\n" in reference) else 4.0

        composite = (sim * 0.6) + (length_score * 0.3) + 0.1
        composite = round(max(0.0, min(1.0, composite)), 4)

        return {
            "score": composite,
            "dimensions": {
                "correctness": round(correctness, 2),
                "adherence": round(adherence, 2),
                "completeness": round(completeness, 2),
                "formatting": round(formatting, 2),
            },
            "reasoning": f"Deterministic heuristic evaluation: semantic={sim:.2f}, length_ratio={length_score:.2f}.",
            "method": "heuristic_judge",
        }
