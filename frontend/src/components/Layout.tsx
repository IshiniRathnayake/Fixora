import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          Fix<span>ora</span>
        </div>
        <nav>
          <NavLink to="/" end className="nav-link">
            Dashboard
          </NavLink>
          <NavLink to="/alerts" className="nav-link">
            Alerts
          </NavLink>
          <NavLink to="/logs" className="nav-link">
            Logs
          </NavLink>
          <NavLink to="/support" className="nav-link">
            Get Help
          </NavLink>
          <NavLink to="/tickets" className="nav-link">
            Tickets
          </NavLink>
          <NavLink to="/query" className="nav-link">
            Ask Fixora
          </NavLink>
          <NavLink to="/diagnostics" className="nav-link">
            Diagnostics
          </NavLink>
          <NavLink to="/enterprise" className="nav-link">
            Enterprise
          </NavLink>
          <NavLink to="/settings" className="nav-link">
            Settings
          </NavLink>
        </nav>
        <div style={{ marginTop: "auto", fontSize: "0.85rem", color: "var(--muted)" }}>
          <div>{user?.full_name}</div>
          <div style={{ textTransform: "capitalize" }}>{user?.role}</div>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ marginTop: "0.75rem", width: "100%" }}
            onClick={logout}
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
