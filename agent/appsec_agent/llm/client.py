import json
import re
from typing import Any

import httpx

JSON_RE = re.compile(r"\{.*\}", re.DOTALL)
STOP_TOKENS = ["<|endoftext|>", "<|im_start|>", "<|im_end|>"]


class LLMClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "local-dev-key",
        timeout: int = 120,
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def health(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(self.base_url.replace("/v1", "/api/tags"))
            return {"ok": response.status_code < 500, "status_code": response.status_code}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    async def chat_json(self, system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
            "stop": STOP_TOKENS,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return parse_json_response(content)
        except Exception:
            return fallback


def clean_text(text: str) -> str:
    cleaned = text.strip()
    for token in STOP_TOKENS:
        cleaned = cleaned.replace(token, "")
    cleaned = cleaned.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    return cleaned


def parse_json_response(text: str) -> dict[str, Any]:
    cleaned = clean_text(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = JSON_RE.search(cleaned)
        if not match:
            raise
        return json.loads(match.group(0))
