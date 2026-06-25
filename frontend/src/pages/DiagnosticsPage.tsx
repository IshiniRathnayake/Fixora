import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { EmptyState, PageHeader } from "../components/ui";
import { useAuth } from "../context/AuthContext";

type Diagnostic = {
  id: number;
  root_cause: string;
  explanation: string;
  remediation?: string;
  confidence?: number;
  created_at: string;
};

export default function DiagnosticsPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<Diagnostic[]>([]);

  useEffect(() => {
    if (!token) return;
    apiFetch<Diagnostic[]>("/api/v1/diagnostics/?limit=30", {}, token).then(setItems).catch(console.error);
  }, [token]);

  return (
    <>
      <PageHeader title="Diagnostics" subtitle="Plain-English root-cause reports (FR2)" />
      {items.map((d) => (
        <div key={d.id} className="panel">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
            <strong style={{ fontSize: "1.05rem" }}>{d.root_cause}</strong>
            {d.confidence != null && (
              <span className="badge badge-high">{Math.round(d.confidence * 100)}% confidence</span>
            )}
          </div>
          <p className="text-muted" style={{ marginTop: "0.5rem" }}>
            {d.explanation}
          </p>
          {d.remediation && (
            <div className="remediation-box">
              <strong>Suggested remediation:</strong> {d.remediation}
            </div>
          )}
          <p className="text-muted" style={{ marginTop: "0.5rem", fontSize: "0.8rem" }}>
            {new Date(d.created_at).toLocaleString()}
          </p>
        </div>
      ))}
      {!items.length && <EmptyState message="No diagnostics yet. Run analysis from the Logs page." />}
    </>
  );
}
