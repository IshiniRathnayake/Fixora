"""Grok (xAI) client for NLP orchestration and diagnostic generation."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import get_settings


class GrokClient:
    """Thin wrapper around xAI chat completions API."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(self.settings.xai_api_key)

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        if not self.is_configured:
            return self._fallback_response(user_prompt)

        payload = {
            "model": self.settings.xai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.xai_api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.settings.xai_base_url.rstrip('/')}/chat/completions"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    def _fallback_response(self, user_prompt: str) -> str:
        """Deterministic fallback when API key is not set (development/demo)."""
        if "sql" in user_prompt.lower() or "select" in user_prompt.lower():
            return "SELECT id, order_ref, status, total_amount FROM orders ORDER BY created_at DESC LIMIT 10;"
        return json.dumps(
            {
                "root_cause": "Elevated error rate in database transaction logs",
                "explanation": (
                    "Multiple ERROR-level log entries suggest contention on write "
                    "operations. This pattern often indicates lock waits or deadlocks."
                ),
                "remediation": (
                    "Review transaction isolation levels and indexes on frequently "
                    "updated tables. Consider shortening transaction scope."
                ),
                "confidence": 0.72,
            }
        )


def extract_sql(text: str) -> str | None:
    """Pull first SELECT statement from model output."""
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    match = re.search(r"(SELECT\b[\s\S]+?;)", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_diagnostic_json(text: str) -> dict[str, Any]:
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
    return {
        "root_cause": "Anomaly detected in operational logs",
        "explanation": text[:500],
        "remediation": "Review recent alerts and correlated log windows.",
        "confidence": 0.5,
    }
