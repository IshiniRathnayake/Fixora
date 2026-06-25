import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { EmptyState, PageHeader, StatusPill } from "../components/ui";
import { useAuth } from "../context/AuthContext";

type Order = {
  id: number;
  order_ref: string;
  customer_name: string;
  status: string;
  total_amount: number;
};

export default function EnterprisePage() {
  const { token, isAdmin } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [msg, setMsg] = useState("");

  const load = useCallback(() => {
    if (!token) return;
    apiFetch<Order[]>("/api/v1/enterprise/orders", {}, token).then(setOrders).catch(console.error);
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  async function processOrder(id: number) {
    if (!token || !isAdmin) return;
    setMsg("");
    try {
      const res = await apiFetch<{ log_message: string }>(
        `/api/v1/enterprise/orders/${id}/process`,
        { method: "POST" },
        token
      );
      setMsg(res.log_message);
      load();
    } catch (e) {
      setMsg(String(e));
    }
  }

  return (
    <>
      <PageHeader
        title="Enterprise app"
        subtitle="Sample ERP orders — processing emits logs monitored by Fixora"
      />
      {msg && (
        <div className="panel">
          <pre className="mono" style={{ border: "none", padding: 0, background: "transparent" }}>
            {msg}
          </pre>
        </div>
      )}
      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Ref</th>
              <th>Customer</th>
              <th>Status</th>
              <th>Amount</th>
              {isAdmin && <th>Action</th>}
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>{o.order_ref}</td>
                <td>{o.customer_name}</td>
                <td>
                  <StatusPill status={o.status} />
                </td>
                <td>£{Number(o.total_amount).toFixed(2)}</td>
                {isAdmin && (
                  <td>
                    <button className="btn btn-secondary" type="button" onClick={() => processOrder(o.id)}>
                      Process
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        {!orders.length && <EmptyState message="No orders in database." />}
      </div>
    </>
  );
}
