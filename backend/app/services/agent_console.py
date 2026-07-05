"""
LM Studio-style terminal renderer for the Fixora multi-agent pipeline.

Prints a clean, colored, boxed trace of each agent as it runs so the
workflow is easy to follow live in the terminal during demos.
"""

from __future__ import annotations

import ctypes
import os
import re
import sys
import textwrap
from typing import Any

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _vlen(text: str) -> int:
    """Visible length of a string, ignoring ANSI escape codes."""
    return len(_ANSI_RE.sub("", text))

# ---- ANSI palette -------------------------------------------------------
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
GRAY = "\033[90m"
RED = "\033[31m"

_WIDTH = 70
_LABEL_COL = 52


def enable() -> None:
    """Enable ANSI colors + UTF-8 output on Windows terminals."""
    if os.name == "nt":
        try:
            kernel32 = ctypes.windll.kernel32
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x4 (| default 0x3)
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass


def _p(text: str = "") -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def _fmt_duration(ms: float) -> str:
    if ms < 1:
        return "<1ms"
    if ms < 1000:
        return f"{int(ms)}ms"
    return f"{ms / 1000:.1f}s"


def _box_line(content: str, color: str) -> str:
    """Render '│ content ... │' padded to the visible inner width."""
    inner = _WIDTH - 4
    pad = max(0, inner - _vlen(content))
    return f"{color}│{RESET} {content}{' ' * pad} {color}│{RESET}"


def header(source: str, issue: str) -> None:
    issue = issue.strip().replace("\n", " ")
    if _vlen(issue) > _WIDTH - 12:
        issue = issue[: _WIDTH - 15] + "..."
    top = "╭" + "─" * (_WIDTH - 2) + "╮"
    bot = "╰" + "─" * (_WIDTH - 2) + "╯"
    _p()
    _p(f"{CYAN}{top}{RESET}")
    _p(_box_line(f"{BOLD}FIXORA{RESET} {DIM}· Multi-Agent Issue Resolution{RESET}", CYAN))
    _p(_box_line(f"{GRAY}source:{RESET} {source}", CYAN))
    _p(_box_line(f"{GRAY}issue :{RESET} {issue}", CYAN))
    _p(f"{CYAN}{bot}{RESET}")


def phase(num: int, title: str, providers: list[str]) -> None:
    tag = " · ".join(providers)
    line = f"  {BOLD}{BLUE}PHASE {num}{RESET} {BOLD}· {title}{RESET}"
    plain_len = len(f"  PHASE {num} · {title}")
    pad = max(2, _WIDTH - plain_len - len(tag) - 4)
    _p()
    _p(f"{line}{' ' * pad}{DIM}[ {tag} ]{RESET}")
    _p(f"  {GRAY}{'─' * (_WIDTH - 2)}{RESET}")


def start(agent: str) -> None:
    label = f"   ▸ {agent}"
    pad = max(2, _LABEL_COL - len(label))
    _p(f"   {YELLOW}▸{RESET} {agent}{' ' * pad}{DIM}running …{RESET}")


def done(agent: str, ms: float, *, failed: bool = False) -> None:
    symbol = f"{RED}✗{RESET}" if failed else f"{GREEN}✔{RESET}"
    state = "failed" if failed else "done"
    label = f"   ✔ {agent}"
    pad = max(2, _LABEL_COL - len(label))
    _p(f"   {symbol} {BOLD}{agent}{RESET}{' ' * pad}{DIM}{state} · {_fmt_duration(ms)}{RESET}")


def field(key: str, value: Any) -> None:
    value = str(value)
    if len(value) > _WIDTH - 22:
        value = value[: _WIDTH - 25] + "..."
    _p(f"       {GRAY}{key:<13}{RESET} {value}")


def steps(items: list[Any]) -> None:
    _p(f"       {GRAY}steps{RESET}")
    for i, step in enumerate(items, 1):
        text = str(step).replace("\n", " ")
        wrapped = textwrap.fill(
            text,
            width=_WIDTH - 4,
            initial_indent=f"         {i}. ",
            subsequent_indent="            ",
        )
        _p(f"{wrapped}")


def articles(items: list[dict]) -> None:
    _p(f"       {GRAY}knowledge{RESET}  {len(items)} article(s)")
    for art in items:
        _p(f"         {MAGENTA}•{RESET} {art.get('title', '?')} {DIM}({art.get('category', '?')}){RESET}")


def ticket(ticket_id: int, priority: str, team: str) -> None:
    title = f"TICKET #{ticket_id} created"
    meta = f"priority: {priority} · team: {team}"
    dashes = max(2, _WIDTH - 6 - len(title))
    top = "╭── " + title + " " + "─" * dashes + "╮"
    bot = "╰" + "─" * (_WIDTH - 2) + "╯"
    _p()
    _p(f"{YELLOW}{top}{RESET}")
    _p(_box_line(meta, YELLOW))
    _p(f"{YELLOW}{bot}{RESET}")


def note(text: str) -> None:
    _p(f"   {GRAY}{text}{RESET}")


def footer(ms: float, category: str, confidence: float) -> None:
    _p()
    _p(
        f"  {GREEN}{BOLD}✔ PIPELINE COMPLETE{RESET} {DIM}·{RESET} "
        f"{_fmt_duration(ms)} {DIM}·{RESET} category={CYAN}{category}{RESET} "
        f"{DIM}·{RESET} confidence={CYAN}{int(confidence * 100)}%{RESET}"
    )
    _p()


enable()
