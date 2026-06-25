"""
Ingest log CSV (Kaggle-style) into Fixora MySQL.

Usage:
  python scripts/ingest_csv_logs.py path/to/logs.csv [--limit 10000]

Expected columns (flexible): timestamp/time/date, level, message/content/log
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.db.session import SessionLocal
from app.models.entities import LogEntry
from app.services.log_parser import LogParserService


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lower = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name in lower:
            return lower[name]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest CSV logs into Fixora")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--limit", type=int, default=10000)
    parser.add_argument("--source-id", type=int, default=3)
    args = parser.parse_args()

    df = pd.read_csv(args.csv_path, nrows=args.limit)
    ts_col = _pick_column(df, ["timestamp", "time", "date", "datetime", "logged_at"])
    level_col = _pick_column(df, ["level", "severity", "log_level"])
    msg_col = _pick_column(df, ["message", "content", "log", "text", "line"])

    if not msg_col:
        msg_col = df.columns[-1]

    log_parser = LogParserService()
    db = SessionLocal()
    stored = 0

    for _, row in df.iterrows():
        message = str(row[msg_col])[:4000]
        level = str(row[level_col]).upper()[:16] if level_col and pd.notna(row[level_col]) else "INFO"
        if level == "WARNING":
            level = "WARN"
        logged_at = datetime.utcnow()
        if ts_col and pd.notna(row[ts_col]):
            try:
                logged_at = pd.to_datetime(row[ts_col]).to_pydatetime()
            except Exception:
                pass
        parsed = log_parser.parse_line(message, default_time=logged_at)
        db.add(
            LogEntry(
                source_id=args.source_id,
                logged_at=logged_at,
                level=level if level in ("DEBUG", "INFO", "WARN", "ERROR", "FATAL") else parsed.level,
                message=message,
                template_id=parsed.template_id,
                raw_line=message,
            )
        )
        stored += 1
        if stored % 500 == 0:
            db.commit()
            print(f"  … {stored} rows")

    db.commit()
    db.close()
    print(f"Ingested {stored} log entries from {args.csv_path}")


if __name__ == "__main__":
    main()
