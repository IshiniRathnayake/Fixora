import { FormEvent, useState } from "react";
import { apiFetch } from "../api/client";
import { DiagnosticBanner, PageHeader } from "../components/ui";
import { useAuth } from "../context/AuthContext";

type NLResponse = {
  natural_language: string;
  generated_sql: string | null;
  is_valid_sql: boolean;
  rows: Record<string, unknown>[];
  row_count: number;
  latency_ms: number;
  error?: string;
};

type AnalyzeResult = {
  context?: {
    diagnostic?: {
      root_cause: string;
      explanation: string;
      remediation?: string;
    };
  };
  nl_query?: { output: NLResponse; duration_ms?: number };
  total_latency_ms?: number;
};

const SUGGESTIONS = [
  "What caused the database slowdown in the last hour?",
  "Show me all failed orders",
  "List inventory items with zero quantity",
];

export default function QueryPage() {
  const { token } = useAuth();
  const [question, setQuestion] = useState(SUGGESTIONS[0]);
  const [nlResult, setNlResult] = useState<NLResponse | null>(null);
  const [fullResult, setFullResult] = useState<AnalyzeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"full" | "query">("full");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    setNlResult(null);
    setFullResult(null);
    try {
      if (mode === "query") {
        setNlResult(await apiFetch<NLResponse>("/api/v1/agents/query", { method: "POST", body: JSON.stringify({ question }) }, token));
      } else {
        const res = await apiFetch<AnalyzeResult>(
          "/api/v1/agents/analyze",
          { method: "POST", body: JSON.stringify({ limit: 500, question }) },
          token
        );
        setFullResult(res);
        const wrap = res.nl_query;
        if (wrap?.output) {
          setNlResult({
            ...wrap.output,
            natural_language: wrap.output.natural_language || question,
            latency_ms: wrap.duration_ms ?? res.total_latency_ms ?? 0,
          });
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const diagnostic = fullResult?.context?.diagnostic;

  return (
    <>
      <PageHeader title="Ask Fixora" subtitle="Natural language queries and full diagnostic pipeline (FR2 + FR3)" />

      <div className="panel" style={{ marginBottom: "1rem" }}>
        <label style={{ marginRight: "1.25rem", fontSize: "14px" }}>
          <input type="radio" checked={mode === "full"} onChange={() => setMode("full")} /> Full diagnostic
        </label>
        <label style={{ fontSize: "14px" }}>
          <input type="radio" checked={mode === "query"} onChange={() => setMode("query")} /> Data query only
        </label>
      </div>

      <div className="panel">
        <form onSubmit={handleSubmit}>
          <textarea
            className="textarea"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask in plain English…"
          />
          <div className="chips">
            {SUGGESTIONS.map((s) => (
              <button key={s} type="button" className="btn btn-secondary" onClick={() => setQuestion(s)}>
                {s.length > 42 ? `${s.slice(0, 42)}…` : s}
              </button>
            ))}
          </div>
          <button className="btn" type="submit" disabled={loading}>
            {loading ? "Processing…" : mode === "full" ? "Run full diagnostic" : "Run query"}
          </button>
        </form>
      </div>

      {diagnostic && (
        <DiagnosticBanner
          title="AI diagnosis"
          rootCause={diagnostic.root_cause}
          explanation={diagnostic.explanation}
          remediation={diagnostic.remediation}
          meta={fullResult?.total_latency_ms ? `Pipeline: ${fullResult.total_latency_ms} ms` : undefined}
        />
      )}

      {nlResult && (
        <>
          <div className="panel">
            <h2 className="panel-title">Generated SQL</h2>
            <pre className="mono">{nlResult.generated_sql ?? nlResult.error}</pre>
            <p className="text-muted" style={{ marginTop: "0.5rem" }}>
              {nlResult.is_valid_sql ? "Valid" : "Invalid"} · {nlResult.row_count} rows · {nlResult.latency_ms} ms
            </p>
          </div>
          {nlResult.rows.length > 0 && (
            <div className="panel">
              <table className="table">
                <thead>
                  <tr>{Object.keys(nlResult.rows[0]).map((k) => <th key={k}>{k}</th>)}</tr>
                </thead>
                <tbody>
                  {nlResult.rows.map((row, i) => (
                    <tr key={i}>
                      {Object.values(row).map((v, j) => (
                        <td key={j}>{String(v)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </>
  );
}
