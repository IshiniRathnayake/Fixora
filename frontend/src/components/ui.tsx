import { ReactNode } from "react";

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle?: string;
  action?: ReactNode;
}) {
  return (
    <>
      <div className="page-header">
        <h1 className="page-title" style={{ marginBottom: 0 }}>
          {title}
        </h1>
        {action}
      </div>
      {subtitle && <p className="page-subtitle">{subtitle}</p>}
    </>
  );
}

export function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card">
      <div className="card-label">{label}</div>
      <div className="card-value">{value}</div>
    </div>
  );
}

export function SeverityBadge({ severity }: { severity: string }) {
  const cls =
    severity === "critical" ? "badge-critical" : severity === "low" ? "badge" : "badge-high";
  return <span className={`badge ${cls}`}>{severity}</span>;
}

export function DiagnosticBanner({
  title,
  rootCause,
  explanation,
  remediation,
  meta,
}: {
  title?: string;
  rootCause: string;
  explanation: string;
  remediation?: string;
  meta?: string;
}) {
  return (
    <div className="diagnostic-banner">
      {title && <h2 className="panel-title">{title}</h2>}
      <p>
        <strong>Root cause:</strong> {rootCause}
      </p>
      <p className="text-muted" style={{ marginTop: "0.5rem" }}>
        {explanation}
      </p>
      {remediation && (
        <p style={{ marginTop: "0.75rem" }}>
          <strong>Suggested fix:</strong> {remediation}
        </p>
      )}
      {meta && (
        <p className="text-muted" style={{ marginTop: "0.5rem", fontSize: "0.85rem" }}>
          {meta}
        </p>
      )}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return <p className="text-muted">{message}</p>;
}

export function StatusPill({ status }: { status: string }) {
  const map: Record<string, string> = {
    completed: "badge-success",
    failed: "badge-critical",
    processing: "badge-processing",
  };
  return <span className={`badge ${map[status] ?? "badge-high"}`}>{status}</span>;
}
