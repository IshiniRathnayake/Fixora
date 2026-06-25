import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { useAuth } from "./context/AuthContext";
import AlertsPage from "./pages/AlertsPage";
import DashboardPage from "./pages/DashboardPage";
import DiagnosticsPage from "./pages/DiagnosticsPage";
import EnterprisePage from "./pages/EnterprisePage";
import LoginPage from "./pages/LoginPage";
import LogsPage from "./pages/LogsPage";
import QueryPage from "./pages/QueryPage";
import SettingsPage from "./pages/SettingsPage";

function Protected({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <Protected>
            <Layout>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/logs" element={<LogsPage />} />
                <Route path="/query" element={<QueryPage />} />
                <Route path="/diagnostics" element={<DiagnosticsPage />} />
                <Route path="/enterprise" element={<EnterprisePage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Layout>
          </Protected>
        }
      />
    </Routes>
  );
}
