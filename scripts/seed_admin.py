"""Seed demo users — also runs automatically on API startup."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.startup import init_db

if __name__ == "__main__":
    init_db()
    print("Database initialized. Users: admin@fixora.local / admin123, viewer@fixora.local / viewer123")
