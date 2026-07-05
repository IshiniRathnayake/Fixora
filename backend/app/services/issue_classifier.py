"""Rule-based issue classifier for fast known-scenario routing."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    category: str
    priority: str
    confidence: float
    matched_patterns: list[str]
    route: str  # "known_model" | "ai_fallback"


CATEGORY_PATTERNS: dict[str, list[str]] = {
    "login_access": [
        r"password",
        r"locked",
        r"cannot\s+log\s*in",
        r"sign\s*in",
        r"expired",
        r"credentials",
    ],
    "permission": [
        r"access\s+denied",
        r"403",
        r"forbidden",
        r"unauthorized",
        r"permission",
    ],
    "network_vpn": [
        r"\bvpn\b",
        r"network",
        r"wifi",
        r"internet",
        r"connection",
    ],
    "email": [
        r"outlook",
        r"email",
        r"mailbox",
        r"calendar",
        r"sync",
    ],
    "web_app": [
        r"page",
        r"loading",
        r"blank",
        r"500",
        r"404",
        r"error",
        r"portal",
        r"submit",
        r"form",
    ],
    "device_printer": [
        r"printer",
        r"print",
        r"offline",
    ],
    "device_hardware": [
        r"camera",
        r"microphone",
        r"mic",
        r"webcam",
        r"laptop",
        r"screen",
    ],
}

PRIORITY_KEYWORDS = {
    "critical": ["down", "outage", "everyone", "all users", "production", "cannot work"],
    "high": ["urgent", "blocked", "asap", "deadline"],
    "low": ["minor", "when possible", "cosmetic"],
}


def classify_issue(text: str, page_error: str | None = None) -> ClassificationResult:
    combined = f"{text} {page_error or ''}".lower()
    best_category = "general"
    best_score = 0
    matched: list[str] = []

    for category, patterns in CATEGORY_PATTERNS.items():
        hits = [p for p in patterns if re.search(p, combined, re.I)]
        if len(hits) > best_score:
            best_score = len(hits)
            best_category = category
            matched = hits

    priority = "medium"
    for level, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            priority = level
            break

    confidence = min(0.95, 0.4 + best_score * 0.15) if best_score else 0.35
    route = "known_model" if best_score >= 2 else "ai_fallback"

    return ClassificationResult(
        category=best_category,
        priority=priority,
        confidence=confidence,
        matched_patterns=matched,
        route=route,
    )
