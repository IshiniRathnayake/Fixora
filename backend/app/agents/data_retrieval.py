"""Data Retrieval Agent — interaction layer NL-to-SQL (FR3)."""

from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.services.llm import GrokClient, extract_sql

ALLOWED_TABLES = frozenset({"orders", "inventory", "log_entries", "alerts", "health_metrics"})
FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|GRANT|REVOKE|CREATE)\b",
    re.IGNORECASE,
)


class DataRetrievalAgent(BaseAgent):
    name = "data_retrieval"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.llm = GrokClient()

    async def run(self, context: AgentContext) -> AgentResult:
        started = datetime.utcnow()
        query = context.nl_query or ""

        system_prompt = (
            "You translate natural language into MySQL SELECT queries only. "
            "Use ONLY these tables: orders, inventory, log_entries, alerts, health_metrics. "
            "Never use DDL or DML. Return only the SQL statement."
        )
        user_prompt = (
            f"Database schema:\n{context.schema_ddl}\n\n"
            f"User question: {query}\n\n"
            "Generate a single SELECT query."
        )

        raw = await self.llm.complete(system_prompt, user_prompt)
        sql = extract_sql(raw) or raw.strip()

        validation_error = self._validate_sql(sql)
        rows: list[dict] = []
        is_valid = validation_error is None

        if is_valid:
            try:
                result = self.db.execute(text(sql))
                columns = list(result.keys())
                rows = [dict(zip(columns, row)) for row in result.fetchmany(100)]
            except Exception as exc:  # noqa: BLE001
                validation_error = str(exc)
                is_valid = False

        completed = datetime.utcnow()
        output = {
            "natural_language": query,
            "generated_sql": sql,
            "is_valid_sql": is_valid,
            "error": validation_error,
            "rows": rows,
            "row_count": len(rows),
        }
        context.metadata["nl_result"] = output

        return AgentResult(
            agent_name=self.name,
            status="completed" if is_valid else "failed",
            output=output,
            duration_ms=int((completed - started).total_seconds() * 1000),
            started_at=started,
            completed_at=completed,
        )

    @staticmethod
    def _validate_sql(sql: str) -> str | None:
        if not sql.upper().strip().startswith("SELECT"):
            return "Only SELECT statements are permitted"
        if FORBIDDEN_KEYWORDS.search(sql):
            return "Statement contains forbidden keywords"
        tables = re.findall(r"\bFROM\s+(\w+)", sql, re.IGNORECASE)
        tables += re.findall(r"\bJOIN\s+(\w+)", sql, re.IGNORECASE)
        for table in tables:
            if table.lower() not in ALLOWED_TABLES:
                return f"Table '{table}' is not in the allowed whitelist"
        return None
