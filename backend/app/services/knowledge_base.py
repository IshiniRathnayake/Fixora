"""Built-in knowledge articles for common office IT scenarios."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KnowledgeArticle:
    id: str
    category: str
    title: str
    keywords: list[str]
    steps: list[str]
    escalation_team: str


KNOWLEDGE_ARTICLES: list[KnowledgeArticle] = [
    KnowledgeArticle(
        id="kb-login-001",
        category="login_access",
        title="Account locked or password expired",
        keywords=["password", "locked", "login", "sign in", "cannot log", "expired", "credentials"],
        steps=[
            "Wait 15 minutes if your account was locked after failed attempts.",
            "Use the 'Forgot password' link on the login page.",
            "If using SSO, sign out of all Microsoft/Google sessions and retry.",
            "Contact IT if you still cannot access your account.",
        ],
        escalation_team="Identity & Access",
    ),
    KnowledgeArticle(
        id="kb-perm-001",
        category="permission",
        title="Access denied or 403 forbidden",
        keywords=["access denied", "403", "forbidden", "permission", "unauthorized", "not allowed"],
        steps=[
            "Confirm you are logged in with the correct work account.",
            "Check if you need manager approval for this module.",
            "Try opening the page in a new browser tab.",
            "Request access from your team lead or IT if the role is missing.",
        ],
        escalation_team="Application Support",
    ),
    KnowledgeArticle(
        id="kb-vpn-001",
        category="network_vpn",
        title="VPN connected but internal apps not working",
        keywords=["vpn", "network", "cannot connect", "internal", "portal", "slow"],
        steps=[
            "Disconnect and reconnect VPN.",
            "Restart your browser after VPN connects.",
            "Check if other colleagues have the same issue.",
            "Try a different network (e.g. mobile hotspot) to rule out local firewall.",
        ],
        escalation_team="Network Operations",
    ),
    KnowledgeArticle(
        id="kb-email-001",
        category="email",
        title="Email or Outlook not syncing",
        keywords=["email", "outlook", "sync", "mailbox", "calendar", "teams"],
        steps=[
            "Close and reopen Outlook or your mail app.",
            "Check Microsoft 365 service status.",
            "Sign out and sign back into your work account.",
            "Clear cached credentials in Windows Credential Manager if needed.",
        ],
        escalation_team="Messaging Support",
    ),
    KnowledgeArticle(
        id="kb-browser-001",
        category="web_app",
        title="Web page stuck loading or blank screen",
        keywords=["loading", "blank", "stuck", "spinning", "white screen", "timeout", "500", "error"],
        steps=[
            "Hard refresh the page (Ctrl+Shift+R).",
            "Disable browser extensions temporarily.",
            "Try another browser (Edge or Chrome).",
            "Clear site cookies for this application only.",
        ],
        escalation_team="Application Support",
    ),
    KnowledgeArticle(
        id="kb-printer-001",
        category="device_printer",
        title="Printer offline or not printing",
        keywords=["printer", "print", "offline", "paper", "queue"],
        steps=[
            "Check printer power and network cable/Wi-Fi.",
            "Open Printers & scanners and set the correct default printer.",
            "Clear the print queue and retry.",
            "Reinstall the printer driver if the issue persists.",
        ],
        escalation_team="Desktop Support",
    ),
    KnowledgeArticle(
        id="kb-device-001",
        category="device_hardware",
        title="Camera or microphone not working",
        keywords=["camera", "microphone", "mic", "webcam", "teams", "zoom", "audio"],
        steps=[
            "Check physical mute switch or camera cover on laptop.",
            "Allow camera/microphone permission in browser settings.",
            "Close other apps that may be using the camera.",
            "Restart the video conferencing app.",
        ],
        escalation_team="Desktop Support",
    ),
]


def search_knowledge(text: str, category: str | None = None, limit: int = 3) -> list[dict]:
    """Keyword-based knowledge retrieval (RAG-lite for demo)."""
    lowered = text.lower()
    scored: list[tuple[int, KnowledgeArticle]] = []

    for article in KNOWLEDGE_ARTICLES:
        if category and article.category != category:
            continue
        score = sum(1 for kw in article.keywords if kw in lowered)
        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, article in scored[:limit]:
        results.append(
            {
                "id": article.id,
                "category": article.category,
                "title": article.title,
                "steps": article.steps,
                "escalation_team": article.escalation_team,
                "relevance_score": score,
            }
        )
    return results
