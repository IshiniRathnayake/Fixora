import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import { EmptyState, MetricCard, PageHeader, SeverityBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";

type Summary = {
  open_alerts: number;
  anomalies_24h: number;
  avg_response_ms: number;
  system_health_score: number;
  recent_alerts: { id: number; severity: string; title: string; summary: string; status: string }[];
  recent_diagnostics: {
    id: number;
    root_cause: string;
    explanation: string;
    remediation?: string;
    confidence?: number;
  }[];
  agent_activity: { agent: string; status: string; duration_ms?: number }[];
};

export default function DashboardPage() {
  const { token } = useAuth();
  const [data, setData] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(() => {
    if (!token) return;
    setLoading(true);
    apiFetch<Summary>("/api/v1/dashboard/summary", {}, token)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    load();
    const id = setInterval(load, 30000);
    return () => clearInterval(id);
  }, [load]);

  return (
    <>
      <PageHeader
        title="System health"
        subtitle="Unified view of agents, alerts, and diagnostics (FR4)"
        action={
          <button className="btn btn-secondary" type="button" onClick={load} disabled={loading}>
            {loading ? "Refreshing…" : "Refresh"}
          </button>
        }
      />

      <p className="quick-links">
        <Link to="/logs">Run log analysis</Link> · <Link to="/query">Ask a question</Link> ·{" "}
        <Link to="/diagnostics">All diagnostics</Link>
      </p>

      <div className="card-grid">
        <MetricCard label="Health score" value={data ? Math.round(data.system_health_score) : "—"} />
        <MetricCard label="Open alerts" value={data?.open_alerts ?? "—"} />
        <MetricCard label="Anomalies (24h)" value={data?.anomalies_24h ?? "—"} />
        <MetricCard
          label="Avg query latency"
          value={data ? `${Math.round(data.avg_response_ms)}ms` : "—"}
        />
      </div>

      <div className="panel">
        <h2 className="panel-title">Recent diagnostics</h2>
        {!data?.recent_diagnostics?.length && (
          <EmptyState message="No diagnostics yet. Run analysis from Logs." />
        )}
        {data?.recent_diagnostics?.map((d) => (
          <div key={d.id} className="diagnostic-item">
            <strong>{d.root_cause}</strong>
            <p className="text-muted">{d.explanation}</p>
            {d.remediation && (
              <p style={{ marginTop: "0.5rem", fontSize: "0.9rem" }}>
                <strong>Fix:</strong> {d.remediation}
              </p>
            )}
          </div>
        ))}
      </div>

      <div className="two-col">
        <div className="panel">
          <h2 className="panel-title">Recent alerts</h2>
          {!data?.recent_alerts?.length && <EmptyState message="No alerts yet." />}
          <ul className="alert-list">
            {data?.recent_alerts?.map((a) => (
              <li key={a.id}>
                <SeverityBadge severity={a.severity} /> {a.title}
              </li>
            ))}
          </ul>
        </div>
        <div className="panel">
          <h2 className="panel-title">Agent activity</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Agent</th>
                <th>Status</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {data?.agent_activity?.map((a, i) => (
                <tr key={i}>
                  <td>{a.agent}</td>
                  <td>{a.status}</td>
                  <td>{a.duration_ms != null ? `${a.duration_ms} ms` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
