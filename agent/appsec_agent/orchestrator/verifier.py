from typing import Any

from appsec_agent.llm.client import LLMClient
from appsec_agent.llm.prompts import VERIFIER_SYSTEM


def deterministic_verify(observation: dict[str, Any]) -> dict[str, Any]:
    evidence_ids = observation.get("evidence_ids") or []
    if observation.get("reproduced") and evidence_ids:
        return {
            "status": "confirmed",
            "confidence": min(float(observation.get("confidence", 0.84)), 0.95),
            "reason": observation.get("reason", "Verifier confirmed the behavior from reproducible sandbox evidence."),
            "evidence_ids": evidence_ids,
            "limitations": "Valid only for the authorized local or staging scope used during this scan.",
        }
    if evidence_ids:
        return {
            "status": "needs_review",
            "confidence": 0.55,
            "reason": "Evidence was collected, but reproducibility or expected policy comparison was incomplete.",
            "evidence_ids": evidence_ids,
            "limitations": "Manual review is required before treating this as confirmed.",
        }
    return {"status": "unconfirmed", "confidence": 0.2, "reason": "No sufficient evidence.", "evidence_ids": [], "limitations": "No validated observation."}


class Verifier:
    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm

    async def verify(self, observation: dict[str, Any]) -> dict[str, Any]:
        fallback = deterministic_verify(observation)
        if not self.llm:
            return fallback
        return await self.llm.chat_json(VERIFIER_SYSTEM, str(observation), fallback=fallback)
