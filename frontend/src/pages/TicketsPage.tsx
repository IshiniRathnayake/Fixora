import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { EmptyState, PageHeader, SeverityBadge } from "../components/ui";
import { useAuth } from "../context/AuthContext";

type Ticket = {
  id: number;
  title: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  source: string;
  page_url: string | null;
  ai_summary: string | null;
  suggested_resolution: string | null;
  model_confidence: number | null;
  assigned_team: string | null;
  created_at: string;
};

export default function TicketsPage() {
  const { token, user } = useAuth();
  const [myTickets, setMyTickets] = useState<Ticket[]>([]);
  const [queue, setQueue] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const isAdmin = user?.role === "administrator";

  useEffect(() => {
    if (!token) return;
    async function load() {
      setLoading(true);
      try {
        const mine = await apiFetch<Ticket[]>("/api/v1/support/tickets/me", {}, token);
        setMyTickets(mine);
        if (isAdmin) {
          const q = await apiFetch<Ticket[]>("/api/v1/support/tickets/queue", {}, token);
          setQueue(q);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [token, isAdmin]);

  async function resolveTicket(id: number) {
    if (!token) return;
    await apiFetch(`/api/v1/support/tickets/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "resolved" }),
    }, token);
    setQueue((q) => q.filter((t) => t.id !== id));
  }

  function TicketTable({ tickets, showActions }: { tickets: Ticket[]; showActions?: boolean }) {
    if (tickets.length === 0) return <EmptyState message="No tickets yet." />;
    return (
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Category</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Team</th>
              <th>Source</th>
              {showActions && <th>Action</th>}
            </tr>
          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.id}>
                <td>#{t.id}</td>
                <td>
                  <div>{t.title}</div>
                  {t.ai_summary && (
                    <div className="text-muted" style={{ fontSize: "0.8rem" }}>
                      {t.ai_summary.slice(0, 80)}…
                    </div>
                  )}
                </td>
                <td>{t.category.replace(/_/g, " ")}</td>
                <td>
                  <SeverityBadge severity={t.priority} />
                </td>
                <td>{t.status}</td>
                <td>{t.assigned_team || "—"}</td>
                <td>{t.source}</td>
                {showActions && (
                  <td>
                    <button type="button" className="btn btn-secondary" onClick={() => resolveTicket(t.id)}>
                      Resolve
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <>
      <PageHeader
        title="Support Tickets"
        subtitle={isAdmin ? "Your tickets and IT helpdesk queue" : "Your submitted support tickets"}
      />

      {loading ? (
        <p className="text-muted">Loading tickets…</p>
      ) : (
        <>
          <div className="panel" style={{ marginBottom: "1.5rem" }}>
            <h3 className="panel-title">My Tickets</h3>
            <TicketTable tickets={myTickets} />
          </div>

          {isAdmin && (
            <div className="panel">
              <h3 className="panel-title">IT Helpdesk Queue</h3>
              <TicketTable tickets={queue} showActions />
            </div>
          )}
        </>
      )}
    </>
  );
}
