import { FormEvent, useState } from "react";
import { apiFetch } from "../api/client";
import { PageHeader, SeverityBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";

type AgentRun = {
  agent: string;
  status: string;
  duration_ms: number;
  output: Record<string, unknown>;
};

type AnalyzeResponse = {
  resolution: {
    summary?: string;
    likely_cause?: string;
    steps?: string[];
    confidence?: number;
    can_self_resolve?: boolean;
  };
  category: string;
  priority: string;
  confidence: number;
  can_self_resolve: boolean;
  knowledge_used: { title: string; steps: string[] }[];
  escalation: { create_ticket?: boolean; reason?: string; assigned_team?: string };
  ticket?: { id: number; title: string; status: string; priority: string };
  workflow: { phases: string[]; agents: AgentRun[] };
};

const EXAMPLES = [
  "I cannot log in to the HR portal. It says my account is locked.",
  "The finance page shows Access Denied when I submit an invoice.",
  "VPN is connected but internal apps are not opening.",
  "Outlook is not syncing my emails since this morning.",
  "The enterprise order page is stuck loading with a 500 error.",
];

export default function SupportPage() {
  const { token } = useAuth();
  const [description, setDescription] = useState(EXAMPLES[0]);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await apiFetch<AnalyzeResponse>(
        "/api/v1/support/analyze",
        {
          method: "POST",
          body: JSON.stringify({ description, source: "web" }),
        },
        token
      );
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Get Help"
        subtitle="Report an office IT issue — Fixora runs a multi-agent workflow (Groq + Gemini) to guide you"
      />

      <div className="panel" style={{ marginBottom: "1.5rem" }}>
        <form onSubmit={handleSubmit}>
          <label className="form-label" htmlFor="issue">
            Describe your problem in plain English
          </label>
          <textarea
            id="issue"
            className="input"
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. I cannot submit the leave form — it shows access denied"
            required
            style={{ width: "100%", marginBottom: "1rem" }}
          />
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                type="button"
                className="btn btn-secondary"
                style={{ fontSize: "0.8rem" }}
                onClick={() => setDescription(ex)}
              >
                {ex.slice(0, 40)}…
              </button>
            ))}
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Analyzing with AI agents…" : "Analyze Issue"}
          </button>
        </form>
      </div>

      {error && (
        <div className="panel" style={{ borderColor: "var(--danger)", marginBottom: "1rem" }}>
          <p style={{ color: "var(--danger)" }}>{error}</p>
        </div>
      )}

      {result && (
        <>
          <div className="card-grid">
            <div className="card">
              <div className="card-label">Category</div>
              <div className="card-value" style={{ fontSize: "1.25rem" }}>
                {result.category.replace(/_/g, " ")}
              </div>
            </div>
            <div className="card">
              <div className="card-label">Priority</div>
              <div className="card-value" style={{ fontSize: "1.25rem" }}>
                <SeverityBadge severity={result.priority} />
              </div>
            </div>
            <div className="card">
              <div className="card-label">Confidence</div>
              <div className="card-value" style={{ fontSize: "1.25rem" }}>
                {Math.round(result.confidence * 100)}%
              </div>
            </div>
            <div className="card">
              <div className="card-label">Self-resolve?</div>
              <div className="card-value" style={{ fontSize: "1.25rem" }}>
                {result.can_self_resolve ? "Yes" : "Escalate"}
              </div>
            </div>
          </div>

          <div className="diagnostic-banner" style={{ marginBottom: "1.5rem" }}>
            <h2 className="panel-title">{result.resolution.summary || "Suggested resolution"}</h2>
            {result.resolution.likely_cause && (
              <p>
                <strong>Likely cause:</strong> {result.resolution.likely_cause}
              </p>
            )}
            {result.resolution.steps && result.resolution.steps.length > 0 && (
              <ol style={{ marginTop: "0.75rem", paddingLeft: "1.25rem" }}>
                {result.resolution.steps.map((step, i) => (
                  <li key={i} style={{ marginBottom: "0.35rem" }}>
                    {step}
                  </li>
                ))}
              </ol>
            )}
          </div>

          {result.ticket && (
            <div className="panel" style={{ marginBottom: "1.5rem", borderColor: "var(--warning)" }}>
              <h3 className="panel-title">IT ticket created</h3>
              <p>
                Ticket #{result.ticket.id}: {result.ticket.title}
              </p>
              <p className="text-muted">
                Assigned to {result.escalation.assigned_team || "IT Helpdesk"} — status: {result.ticket.status}
              </p>
            </div>
          )}

          {result.knowledge_used.length > 0 && (
            <div className="panel" style={{ marginBottom: "1.5rem" }}>
              <h3 className="panel-title">Knowledge articles used</h3>
              {result.knowledge_used.map((kb) => (
                <div key={kb.title} style={{ marginBottom: "0.75rem" }}>
                  <strong>{kb.title}</strong>
                </div>
              ))}
            </div>
          )}

          <div className="panel">
            <h3 className="panel-title">Agent workflow (for demo)</h3>
            <p className="text-muted" style={{ marginBottom: "1rem" }}>
              Phases: {result.workflow.phases.join(" → ")}
            </p>
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Agent</th>
                    <th>Status</th>
                    <th>Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {result.workflow.agents.map((a) => (
                    <tr key={a.agent}>
                      <td style={{ textTransform: "capitalize" }}>{a.agent.replace(/_/g, " ")}</td>
                      <td>{a.status}</td>
                      <td>{a.duration_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </>
  );
}
