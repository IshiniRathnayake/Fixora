"""Log pre-processing: template extraction (Drain3) and feature vectors."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig


@dataclass
class ParsedLogLine:
    logged_at: datetime
    level: str
    message: str
    template_id: str
    template: str


class LogParserService:
    """Source-code-agnostic log parsing using Drain3 (He et al., 2017)."""

    LEVEL_PATTERN = re.compile(
        r"\b(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\b",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        config = TemplateMinerConfig()
        config.drain_sim_th = 0.4
        self._miner = TemplateMiner(config=config)

    def parse_line(self, raw_line: str, default_time: datetime | None = None) -> ParsedLogLine:
        logged_at = default_time or datetime.utcnow()
        level_match = self.LEVEL_PATTERN.search(raw_line)
        level = (level_match.group(1).upper() if level_match else "INFO").replace("WARNING", "WARN")

        result = self._miner.add_log_message(raw_line.strip())
        template_id = str(result["cluster_id"])
        template = result["template_mined"]

        return ParsedLogLine(
            logged_at=logged_at,
            level=level,
            message=raw_line.strip()[:4000],
            template_id=template_id,
            template=template,
        )

    def parse_file(self, path: str) -> list[ParsedLogLine]:
        lines: list[ParsedLogLine] = []
        with open(path, encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                if raw.strip():
                    lines.append(self.parse_line(raw))
        return lines

    @staticmethod
    def build_feature_matrix(df: pd.DataFrame) -> np.ndarray:
        """Numeric features for Isolation Forest / Random Forest."""
        level_map = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "FATAL": 4}
        df = df.copy()
        df["level_num"] = df["level"].map(level_map).fillna(1)
        df["msg_len"] = df["message"].str.len().clip(0, 5000)
        df["template_freq"] = df.groupby("template_id")["template_id"].transform("count")
        return df[["level_num", "msg_len", "template_freq"]].to_numpy(dtype=float)
