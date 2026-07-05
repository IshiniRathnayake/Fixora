"""Groq API client for fast agent tasks (intake, routing, escalation)."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import get_settings


class GroqClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.groq_api_key)

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        if not self.is_configured:
            return self._fallback(user_prompt)

        payload = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.groq_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.settings.groq_base_url.rstrip('/')}/chat/completions"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        text = await self.complete(
            system_prompt + "\nRespond with valid JSON only, no markdown.",
            user_prompt,
            temperature=temperature,
        )
        return parse_json_response(text)

    def _fallback(self, user_prompt: str) -> str:
        return json.dumps(
            {
                "category": "general",
                "urgency": "medium",
                "summary": user_prompt[:200],
                "entities": {},
                "confidence": 0.5,
            }
        )


def parse_json_response(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if fenced:
        return json.loads(fenced.group(1))
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start : end + 1])
    return {"raw": text}
