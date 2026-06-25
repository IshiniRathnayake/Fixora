import { useAuth } from "../context/AuthContext";
import { PageHeader } from "../components/ui";

const PERMISSIONS = [
  { name: "Ingest logs", admin: true, viewer: false },
  { name: "Run analysis pipeline", admin: true, viewer: false },
  { name: "Acknowledge alerts", admin: true, viewer: false },
  { name: "Natural language queries", admin: true, viewer: true },
  { name: "View dashboard", admin: true, viewer: true },
];

export default function SettingsPage() {
  const { user, isAdmin } = useAuth();

  return (
    <>
      <PageHeader title="Settings" subtitle="Role-based access control and account (FR5)" />
      <div className="panel">
        <h2 className="panel-title">Your profile</h2>
        <p className="profile-row">
          <span className="text-muted">Name</span> {user?.full_name}
        </p>
        <p className="profile-row">
          <span className="text-muted">Email</span> {user?.email}
        </p>
        <p className="profile-row">
          <span className="text-muted">Role</span>{" "}
          <span className="badge badge-processing">{user?.role}</span>
        </p>
      </div>
      <div className="panel">
        <h2 className="panel-title">Permissions</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Capability</th>
              <th>Administrator</th>
              <th>Viewer</th>
            </tr>
          </thead>
          <tbody>
            {PERMISSIONS.map((p) => (
              <tr key={p.name}>
                <td>{p.name}</td>
                <td>{p.admin ? "✓" : "—"}</td>
                <td>{p.viewer ? "✓" : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {isAdmin && (
        <div className="panel">
          <h2 className="panel-title">Demo accounts</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Password</th>
                <th>Role</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>admin@fixora.local</td>
                <td className="mono">admin123</td>
                <td>Administrator</td>
              </tr>
              <tr>
                <td>viewer@fixora.local</td>
                <td className="mono">viewer123</td>
                <td>Viewer</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
