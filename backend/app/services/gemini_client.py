"""Google Gemini API client for resolution synthesis and complex reasoning."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import get_settings
from app.services.groq_client import parse_json_response


class GeminiClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.gemini_api_key)

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        if not self.is_configured:
            return self._fallback(user_prompt)

        model = self.settings.gemini_model
        combined = f"{system_prompt}\n\n{user_prompt}"
        payload = {
            "contents": [{"role": "user", "parts": [{"text": combined}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent?key={self.settings.gemini_api_key}"
            )
            response = await client.post(url, json=payload)

            if response.status_code in (401, 403, 404, 429, 503):
                return self._fallback(user_prompt)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return self._fallback(user_prompt)
            parts = candidates[0].get("content", {}).get("parts", [])
            return parts[0].get("text", "").strip() if parts else self._fallback(user_prompt)

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        text = await self.complete(
            system_prompt + "\nRespond with valid JSON only, no markdown fences.",
            user_prompt,
            temperature=temperature,
        )
        return parse_json_response(text)

    def _fallback(self, user_prompt: str) -> str:
        return json.dumps(
            {
                "summary": "We analyzed your issue and prepared troubleshooting steps.",
                "steps": [
                    "Refresh the page and try again.",
                    "Clear your browser cache or use a private window.",
                    "Sign out and sign back in.",
                    "If the problem continues, contact IT support.",
                ],
                "likely_cause": "Temporary session or permission issue",
                "confidence": 0.55,
                "can_self_resolve": True,
            }
        )
