import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { DiagnosticBanner, EmptyState, PageHeader } from "../components/ui";
import { useAuth } from "../context/AuthContext";

type LogRow = {
  id: number;
  logged_at: string;
  level: string;
  message: string;
  is_anomaly: boolean;
  anomaly_score?: number;
};

type AnalyzeResult = {
  context?: {
    anomaly_count: number;
    diagnostic?: {
      root_cause: string;
      explanation: string;
      remediation?: string;
    };
  };
  persisted?: { alerts_created: number };
  total_latency_ms?: number;
  message?: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export default function LogsPage() {
  const { token, isAdmin } = useAuth();
  const [logs, setLogs] = useState<LogRow[]>([]);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadLogs = useCallback(() => {
    if (!token) return;
    apiFetch<LogRow[]>("/api/v1/logs/?limit=100", {}, token)
      .then(setLogs)
      .catch((e) => setError(String(e)));
  }, [token]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  async function ingestSample() {
    if (!token || !isAdmin) return;
    setLoading(true);
    setError("");
    try {
      await apiFetch("/api/v1/logs/ingest/sample", { method: "POST" }, token);
      loadLogs();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function runAnalyze() {
    if (!token) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await apiFetch<AnalyzeResult>(
        "/api/v1/agents/analyze",
        { method: "POST", body: JSON.stringify({ limit: 500 }) },
        token
      );
      setResult(res);
      loadLogs();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function uploadFile(file: File) {
    if (!token || !isAdmin) return;
    const form = new FormData();
    form.append("file", file);
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/v1/logs/ingest`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) throw new Error(await res.text());
      loadLogs();
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  const diagnostic = result?.context?.diagnostic;

  return (
    <>
      <PageHeader
        title="Log monitoring"
        subtitle="Drain3 parsing · Isolation Forest · multi-agent pipeline (FR1)"
      />

      <div className="toolbar">
        {isAdmin && (
          <>
            <button className="btn btn-secondary" type="button" onClick={ingestSample} disabled={loading}>
              1. Load sample logs
            </button>
            <label className="btn btn-secondary" style={{ cursor: "pointer" }}>
              Upload log file
              <input
                type="file"
                accept=".log,.txt"
                hidden
                onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])}
              />
            </label>
          </>
        )}
        <button className="btn" type="button" onClick={runAnalyze} disabled={loading || !logs.length}>
          {loading ? "Analysing…" : "2. Run AI analysis pipeline"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {result?.message && <div className="panel">{result.message}</div>}

      {diagnostic && (
        <DiagnosticBanner
          title="Diagnostic (Analysis Agent)"
          rootCause={diagnostic.root_cause}
          explanation={diagnostic.explanation}
          remediation={diagnostic.remediation}
          meta={
            result?.persisted
              ? `${result.persisted.alerts_created} alert(s) saved · ${result.total_latency_ms ?? 0} ms`
              : undefined
          }
        />
      )}

      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Level</th>
              <th>Message</th>
              <th>Anomaly</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l) => (
              <tr key={l.id} className={l.is_anomaly ? "row-anomaly" : undefined}>
                <td>{l.logged_at ? new Date(l.logged_at).toLocaleString() : "—"}</td>
                <td>{l.level}</td>
                <td>{l.message}</td>
                <td>{l.is_anomaly ? `Yes (${(l.anomaly_score ?? 0).toFixed(2)})` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!logs.length && (
          <EmptyState
            message={
              isAdmin
                ? 'No logs yet. Click "Load sample logs" to begin.'
                : "No logs available. Contact an administrator."
            }
          />
        )}
      </div>
    </>
  );
}
