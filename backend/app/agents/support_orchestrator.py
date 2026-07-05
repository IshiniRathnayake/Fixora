"""
Multi-agent orchestrator for office employee issue resolution.

Workflow:
  Phase 1 (linear):  Intake Agent (Groq) — understand and structure the issue
  Phase 2 (parallel): Scenario Router + Knowledge Search + Context Analyzer
  Phase 3 (linear):  Resolution Agent (Gemini) — synthesize user-friendly fix
  Phase 4 (linear):  Escalation Agent (Groq) — decide ticket + priority
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.agents.support_context import SupportContext
from app.models.entities import AgentRun, SupportTicket
from app.services import agent_console as console
from app.services.gemini_client import GeminiClient
from app.services.groq_client import GroqClient
from app.services.issue_classifier import classify_issue
from app.services.knowledge_base import search_knowledge

logger = logging.getLogger("fixora.agents")


class SupportOrchestrator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.groq = GroqClient()
        self.gemini = GeminiClient()

    async def resolve(self, ctx: SupportContext) -> dict[str, Any]:
        pipeline_start = time.perf_counter()
        console.header(ctx.source, ctx.description)

        console.phase(1, "Intake & Classification", ["Groq", "local"])
        ctx.workflow_phases.append("phase1_intake")
        await self._run_intake(ctx)

        console.phase(2, "Parallel Analysis", ["Groq", "local", "local"])
        ctx.workflow_phases.append("phase2_parallel_analysis")
        await asyncio.gather(
            self._run_scenario_router(ctx),
            self._run_knowledge_agent(ctx),
            self._run_context_analyzer(ctx),
        )

        console.phase(3, "Resolution Synthesis", ["Gemini"])
        ctx.workflow_phases.append("phase3_resolution")
        await self._run_resolution(ctx)

        console.phase(4, "Escalation Decision", ["Groq"])
        ctx.workflow_phases.append("phase4_escalation")
        await self._run_escalation(ctx)

        if ctx.escalation.get("create_ticket"):
            ctx.ticket = self._create_ticket(ctx)
            console.ticket(
                ctx.ticket["id"],
                ctx.ticket["priority"],
                ctx.ticket["assigned_team"] or "IT Helpdesk",
            )
        else:
            console.note("No ticket needed - user can self-resolve")

        total_ms = (time.perf_counter() - pipeline_start) * 1000
        console.footer(
            total_ms,
            ctx.intake.get("category") or ctx.rule_classification.get("category"),
            float(ctx.resolution.get("confidence", 0)),
        )

        return self._build_response(ctx)

    async def _run_intake(self, ctx: SupportContext) -> None:
        started = time.perf_counter()
        console.start("intake")
        system = (
            "You are Fixora Issue Intake Agent. Extract structured data from employee IT issues. "
            "Categories: login_access, permission, network_vpn, email, web_app, device_printer, "
            "device_hardware, software, general. "
            'Return JSON: {"category","urgency","summary","affected_system","entities":{}}'
        )
        try:
            intake = await self.groq.complete_json(system, ctx.to_prompt_context())
        except Exception as exc:
            intake = {"category": "general", "urgency": "medium", "summary": ctx.description, "error": str(exc)}

        rule = classify_issue(ctx.description, ctx.page_error)
        ctx.rule_classification = {
            "category": rule.category,
            "priority": rule.priority,
            "confidence": rule.confidence,
            "route": rule.route,
            "matched_patterns": rule.matched_patterns,
        }
        ctx.intake = intake
        duration = (time.perf_counter() - started) * 1000
        console.done("intake", duration)
        console.field("category", intake.get("category", ctx.rule_classification.get("category")))
        console.field("urgency", intake.get("urgency", "-"))
        console.field("summary", intake.get("summary", "-"))
        console.field("route", ctx.rule_classification.get("route"))
        ctx.agent_runs.append(
            self._agent_run("intake", "completed", int(duration), {"intake": intake, "rule": ctx.rule_classification})
        )
        self._persist_agent_run("support_intake", "user_query", int(duration), ctx.description[:500])

    async def _run_scenario_router(self, ctx: SupportContext) -> None:
        started = time.perf_counter()
        console.start("scenario_router")
        category = ctx.intake.get("category") or ctx.rule_classification.get("category", "general")
        route = ctx.rule_classification.get("route", "ai_fallback")

        if route == "known_model":
            scenario = {
                "route": "known_model",
                "category": category,
                "confidence": ctx.rule_classification.get("confidence", 0.7),
                "message": f"Matched known scenario: {category}",
            }
        else:
            system = (
                "You are Fixora Scenario Router. Decide if this is a known IT scenario or needs deep AI analysis. "
                'Return JSON: {"route":"known_model"|"ai_fallback","category","confidence":0-1,"reason"}'
            )
            try:
                scenario = await self.groq.complete_json(
                    system,
                    f"{ctx.to_prompt_context()}\nRule classification: {ctx.rule_classification}",
                )
            except Exception:
                scenario = {"route": "ai_fallback", "category": category, "confidence": 0.5}

        ctx.scenario = scenario
        duration = (time.perf_counter() - started) * 1000
        console.done("scenario_router", duration)
        console.field("route", scenario.get("route"))
        console.field("confidence", scenario.get("confidence"))
        ctx.agent_runs.append(self._agent_run("scenario_router", "completed", int(duration), scenario))
        self._persist_agent_run("support_scenario_router", "pipeline", int(duration), str(scenario)[:500])

    async def _run_knowledge_agent(self, ctx: SupportContext) -> None:
        started = time.perf_counter()
        console.start("knowledge")
        category = ctx.intake.get("category") or ctx.rule_classification.get("category")
        articles = search_knowledge(ctx.description, category=category if category != "general" else None)
        if not articles:
            articles = search_knowledge(ctx.description)
        ctx.knowledge = articles
        duration = (time.perf_counter() - started) * 1000
        console.done("knowledge", duration)
        console.articles(articles)
        ctx.agent_runs.append(self._agent_run("knowledge", "completed", int(duration), {"articles": articles}))
        self._persist_agent_run("support_knowledge", "pipeline", int(duration), f"found {len(articles)} articles")

    async def _run_context_analyzer(self, ctx: SupportContext) -> None:
        started = time.perf_counter()
        console.start("context_analyzer")
        analysis: dict[str, Any] = {
            "has_page_context": bool(ctx.page_url or ctx.page_title),
            "has_visible_error": bool(ctx.page_error),
            "technical_signals": [],
        }
        if ctx.page_error:
            err = ctx.page_error.lower()
            if "403" in err or "forbidden" in err or "access denied" in err:
                analysis["technical_signals"].append("permission_error")
            if "500" in err or "server error" in err:
                analysis["technical_signals"].append("server_error")
            if "timeout" in err or "loading" in err:
                analysis["technical_signals"].append("performance_issue")

        if ctx.page_url:
            url = ctx.page_url.lower()
            if "/login" in url or "signin" in url:
                analysis["technical_signals"].append("auth_page")
            if "enterprise" in url or "hr" in url or "finance" in url:
                analysis["affected_module"] = "enterprise_web_app"

        ctx.context_analysis = analysis
        duration = (time.perf_counter() - started) * 1000
        console.done("context_analyzer", duration)
        console.field("signals", analysis.get("technical_signals", []) or "none")
        if analysis.get("affected_module"):
            console.field("module", analysis["affected_module"])
        ctx.agent_runs.append(self._agent_run("context_analyzer", "completed", int(duration), analysis))
        self._persist_agent_run("support_context", "pipeline", int(duration), str(analysis)[:500])

    async def _run_resolution(self, ctx: SupportContext) -> None:
        started = time.perf_counter()
        console.start("resolution")
        system = (
            "You are Fixora Resolution Agent for non-technical office employees. "
            "Use provided knowledge articles and analysis to give clear, simple troubleshooting steps. "
            "Avoid jargon. Be specific to the user's page and error if available. "
            'Return JSON: {"summary","likely_cause","steps":["step1",...],"confidence":0-1,'
            '"can_self_resolve":true|false,"estimated_time_minutes":number}'
        )
        user = (
            f"{ctx.to_prompt_context()}\n\n"
            f"Intake: {ctx.intake}\n"
            f"Scenario: {ctx.scenario}\n"
            f"Knowledge articles: {ctx.knowledge}\n"
            f"Context analysis: {ctx.context_analysis}"
        )
        try:
            resolution = await self.gemini.complete_json(system, user)
        except Exception as exc:
            resolution = {
                "summary": "We prepared general troubleshooting steps for your issue.",
                "likely_cause": "Unknown — needs further review",
                "steps": [
                    "Refresh the page and try again.",
                    "Sign out and sign back in.",
                    "Contact IT if the issue continues.",
                ],
                "confidence": 0.4,
                "can_self_resolve": False,
                "error": str(exc),
            }

        ctx.resolution = resolution
        duration = (time.perf_counter() - started) * 1000
        console.done("resolution", duration)
        console.field("confidence", f"{float(resolution.get('confidence', 0)) * 100:.0f}%")
        console.field("likely_cause", resolution.get("likely_cause", "-"))
        console.field("summary", resolution.get("summary", "-"))
        if resolution.get("steps"):
            console.steps(resolution["steps"])
        ctx.agent_runs.append(self._agent_run("resolution", "completed", int(duration), resolution))
        self._persist_agent_run("support_resolution", "pipeline", int(duration), resolution.get("summary", "")[:500])

    async def _run_escalation(self, ctx: SupportContext) -> None:
        started = time.perf_counter()
        console.start("escalation")
        confidence = float(ctx.resolution.get("confidence", 0.5))
        can_self_resolve = ctx.resolution.get("can_self_resolve", True)

        system = (
            "You are Fixora Escalation Agent. Decide if an IT ticket is needed. "
            "Create ticket when: low confidence, cannot self-resolve, critical priority, or permission/server errors. "
            'Return JSON: {"create_ticket":true|false,"priority":"low|medium|high|critical",'
            '"assigned_team","ticket_title","ticket_summary","reason"}'
        )
        user = (
            f"Issue: {ctx.description}\n"
            f"Resolution confidence: {confidence}\n"
            f"Can self resolve: {can_self_resolve}\n"
            f"Category: {ctx.intake.get('category', 'general')}\n"
            f"Context signals: {ctx.context_analysis}\n"
            f"Resolution: {ctx.resolution.get('summary', '')}"
        )
        try:
            escalation = await self.groq.complete_json(system, user)
        except Exception:
            escalation = {
                "create_ticket": confidence < 0.6 or not can_self_resolve,
                "priority": ctx.rule_classification.get("priority", "medium"),
                "assigned_team": "IT Helpdesk",
                "ticket_title": ctx.description[:100],
                "ticket_summary": ctx.resolution.get("summary", ctx.description),
                "reason": "Automatic escalation due to low confidence",
            }

        if confidence < 0.55:
            escalation["create_ticket"] = True
        ctx.escalation = escalation
        duration = (time.perf_counter() - started) * 1000
        console.done("escalation", duration)
        console.field("create_ticket", escalation.get("create_ticket"))
        console.field("priority", escalation.get("priority"))
        console.field("team", escalation.get("assigned_team", "-"))
        console.field("reason", escalation.get("reason", "-"))
        ctx.agent_runs.append(self._agent_run("escalation", "completed", int(duration), escalation))
        self._persist_agent_run("support_escalation", "pipeline", int(duration), str(escalation)[:500])

    def _create_ticket(self, ctx: SupportContext) -> dict[str, Any]:
        esc = ctx.escalation
        ticket = SupportTicket(
            requester_id=ctx.user_id,
            title=esc.get("ticket_title", ctx.description[:120]),
            description=ctx.description,
            category=ctx.intake.get("category") or ctx.rule_classification.get("category", "general"),
            priority=esc.get("priority", "medium"),
            status="open",
            source=ctx.source,
            page_url=ctx.page_url,
            ai_summary=ctx.resolution.get("summary"),
            suggested_resolution="\n".join(ctx.resolution.get("steps", [])),
            model_confidence=float(ctx.resolution.get("confidence", 0.5)),
            assigned_team=esc.get("assigned_team", "IT Helpdesk"),
            agent_trace_json={
                "workflow_phases": ctx.workflow_phases,
                "agent_runs": ctx.agent_runs,
            },
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return {
            "id": ticket.id,
            "title": ticket.title,
            "status": ticket.status,
            "priority": ticket.priority,
            "assigned_team": ticket.assigned_team,
        }

    def _persist_agent_run(self, name: str, trigger: str, duration_ms: int, summary: str) -> None:
        run = AgentRun(
            agent_name=name,
            trigger_type=trigger,
            input_summary=summary[:1000] if summary else None,
            output_summary=summary[:1000] if summary else None,
            status="completed",
            duration_ms=duration_ms,
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(run)

    @staticmethod
    def _agent_run(name: str, status: str, duration_ms: int, output: dict) -> dict[str, Any]:
        return {
            "agent": name,
            "status": status,
            "duration_ms": duration_ms,
            "output": output,
        }

    def _build_response(self, ctx: SupportContext) -> dict[str, Any]:
        self.db.commit()
        return {
            "resolution": ctx.resolution,
            "category": ctx.intake.get("category") or ctx.rule_classification.get("category"),
            "priority": ctx.escalation.get("priority", "medium"),
            "confidence": ctx.resolution.get("confidence", 0.5),
            "can_self_resolve": ctx.resolution.get("can_self_resolve", True),
            "knowledge_used": ctx.knowledge,
            "escalation": ctx.escalation,
            "ticket": ctx.ticket,
            "workflow": {
                "phases": ctx.workflow_phases,
                "agents": ctx.agent_runs,
            },
        }
