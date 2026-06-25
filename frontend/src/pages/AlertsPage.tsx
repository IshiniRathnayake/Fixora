import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { EmptyState, PageHeader, SeverityBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";

type Alert = {
  id: number;
  severity: string;
  title: string;
  summary: string;
  status: string;
  detected_at: string;
};

export default function AlertsPage() {
  const { token, isAdmin } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);

  const load = useCallback(() => {
    if (!token) return;
    apiFetch<Alert[]>("/api/v1/alerts/", {}, token).then(setAlerts).catch(console.error);
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  async function acknowledge(id: number) {
    if (!token || !isAdmin) return;
    await apiFetch(`/api/v1/alerts/${id}/acknowledge`, { method: "PATCH" }, token);
    load();
  }

  return (
    <>
      <PageHeader title="Alerts" subtitle="Contextualised alerts from the Monitoring Agent (FR1)" />
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Title</th>
              <th>Summary</th>
              <th>Status</th>
              <th>Detected</th>
              {isAdmin && <th />}
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.id}>
                <td>
                  <SeverityBadge severity={a.severity} />
                </td>
                <td>{a.title}</td>
                <td style={{ maxWidth: 280 }}>{a.summary}</td>
                <td>{a.status}</td>
                <td>{new Date(a.detected_at).toLocaleString()}</td>
                {isAdmin && (
                  <td>
                    {a.status === "open" && (
                      <button className="btn btn-secondary" type="button" onClick={() => acknowledge(a.id)}>
                        Ack
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        {!alerts.length && (
          <EmptyState message="No alerts. Run AI analysis on the Logs page to generate alerts." />
        )}
      </div>
    </>
  );
}
