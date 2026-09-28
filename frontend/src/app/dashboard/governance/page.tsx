"use client";

import {
  Shield,
  Database,
  Activity,
  CheckCircle,
  AlertTriangle,
  Clock,
  Eye,
  BarChart3,
  RefreshCcw,
  Lock,
  Scale,
} from "lucide-react";

const modelVersions = [
  {
    id: "m1",
    version: "0.1.0-synthetic",
    type: "Discrete-time Hazard (LightGBM)",
    status: "active",
    metrics: { roc_auc: 0.847, pr_auc: 0.723, brier_score: 0.142, calibration_error: 0.038, c_index: 0.812, coverage_90: 0.891 },
    approved_by: "Model Governor",
    approved_on: "2026-09-15",
    training_window: "2020-01-01 to 2026-09-01",
  },
  {
    id: "m2",
    version: "0.0.9-baseline",
    type: "Plain Classifier (Baseline)",
    status: "retired",
    metrics: { roc_auc: 0.782, pr_auc: 0.651, brier_score: 0.187, calibration_error: 0.062 },
    approved_by: "Model Governor",
    approved_on: "2026-08-20",
    training_window: "2020-01-01 to 2026-08-01",
  },
];

const dataSources = [
  { name: "State Land Stack (DILRMP 3.0)", type: "land_stack", health: "healthy", lastSync: "2 min ago", label: "Mock feed with real schema" },
  { name: "Bhoomi Rashi (MoRTH)", type: "acquisition_status", health: "healthy", lastSync: "15 min ago", label: "Mock feed with real schema" },
  { name: "PFMS", type: "payment_system", health: "healthy", lastSync: "1 hour ago", label: "Mock feed with real schema" },
  { name: "NJDG / Court Data", type: "court_data", health: "healthy", lastSync: "6 hours ago", label: "Structured synthetic event stream" },
  { name: "PARIVESH", type: "approval_tracker", health: "healthy", lastSync: "3 hours ago", label: "Mock feed with real schema" },
  { name: "Requiring Body Feed", type: "project_data", health: "healthy", lastSync: "30 min ago", label: "CSV import" },
];

const auditEntries = [
  { actor: "Dr. Priya Sharma", action: "VIEW_PREDICTION", entity: "Project LA-RJ-JAI-0012", time: "2 min ago" },
  { actor: "System", action: "PREDICTION_REFRESH", entity: "127 projects scored", time: "15 min ago" },
  { actor: "Adv. Meera Nair", action: "VIEW_EVIDENCE", entity: "Project LA-MH-PUN-0034", time: "28 min ago" },
  { actor: "System", action: "CLOCK_CHECK", entity: "12 clocks evaluated", time: "30 min ago" },
  { actor: "Ramesh Kumar", action: "ACK_ALERT", entity: "Alert: Court stay detected", time: "1 hour ago" },
  { actor: "Model Governor", action: "MODEL_APPROVED", entity: "v0.1.0-synthetic", time: "14 days ago" },
];

const fairnessMetrics = {
  groups: ["Urban", "Semi-Urban", "Rural", "Tribal"],
  error_rate: [0.14, 0.16, 0.18, 0.19],
  score_dist: [0.52, 0.55, 0.58, 0.61],
};

export default function GovernancePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Governance Dashboard</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
          Data confidence, model performance, drift detection, fairness, audit
        </p>
      </div>

      {/* Model Performance */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold flex items-center gap-2 mb-5">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          Model Performance
        </h2>

        <div className="space-y-4">
          {modelVersions.map((model) => (
            <div
              key={model.id}
              className={`p-5 rounded-xl border ${
                model.status === "active"
                  ? "border-[var(--color-border-active)] bg-[rgba(59,130,246,0.04)]"
                  : "border-[var(--color-border)] opacity-60"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm font-semibold">{model.version}</span>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase ${
                      model.status === "active"
                        ? "bg-green-500/15 text-green-400"
                        : "bg-gray-500/15 text-gray-400"
                    }`}
                  >
                    {model.status}
                  </span>
                </div>
                <div className="text-xs text-[var(--color-text-muted)]">
                  <Lock className="w-3 h-3 inline mr-1" />
                  Approved by {model.approved_by} on {model.approved_on}
                </div>
              </div>

              <p className="text-xs text-[var(--color-text-secondary)] mb-3">{model.type}</p>

              {/* Metrics Grid */}
              <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                {Object.entries(model.metrics).map(([key, value]) => (
                  <div key={key} className="text-center p-2 rounded-lg bg-[rgba(255,255,255,0.02)]">
                    <p className="text-lg font-bold text-[var(--color-text-primary)]">
                      {typeof value === "number" ? value.toFixed(3) : value}
                    </p>
                    <p className="text-[9px] text-[var(--color-text-muted)] uppercase tracking-wider">
                      {key.replace(/_/g, " ")}
                    </p>
                  </div>
                ))}
              </div>

              <p className="text-[10px] text-[var(--color-text-muted)] mt-2">
                Training window: {model.training_window} • Synthetic data
              </p>
            </div>
          ))}
        </div>

        <p className="text-[10px] text-amber-400/80 mt-3 flex items-center gap-1">
          <AlertTriangle className="w-3 h-3" />
          No model reaches production without recorded human approval (FR-20).
          Automatic promotion prohibited.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Data Sources */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-5">
            <Database className="w-5 h-5 text-emerald-400" />
            Data Sources
          </h2>

          <div className="space-y-2">
            {dataSources.map((source, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--color-border)]"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      source.health === "healthy" ? "bg-green-400" : "bg-red-400"
                    }`}
                  />
                  <div>
                    <p className="text-xs font-medium">{source.name}</p>
                    <p className="text-[10px] text-amber-400/70 italic">{source.label}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-[var(--color-text-muted)]">
                  <RefreshCcw className="w-3 h-3" />
                  {source.lastSync}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Fairness Report */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-5">
            <Scale className="w-5 h-5 text-purple-400" />
            Fairness Report
          </h2>

          <table className="data-table">
            <thead>
              <tr>
                <th>District Group</th>
                <th>Error Rate</th>
                <th>Avg Score</th>
                <th>Gap</th>
              </tr>
            </thead>
            <tbody>
              {fairnessMetrics.groups.map((group, i) => {
                const gap = Math.abs(fairnessMetrics.error_rate[i] - fairnessMetrics.error_rate[0]);
                return (
                  <tr key={group}>
                    <td className="text-xs font-medium">{group}</td>
                    <td className="text-xs">{(fairnessMetrics.error_rate[i] * 100).toFixed(1)}%</td>
                    <td className="text-xs">{(fairnessMetrics.score_dist[i] * 100).toFixed(1)}%</td>
                    <td>
                      <span className={`text-xs ${gap > 0.04 ? "text-amber-400" : "text-green-400"}`}>
                        {gap > 0 ? `+${(gap * 100).toFixed(1)}%` : "—"}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <p className="text-[10px] text-[var(--color-text-muted)] mt-3">
            Sensitive attributes (caste, religion) excluded from model features.
            Scheduled-Area status selects template safeguards only.
          </p>
        </div>
      </div>

      {/* Audit Log */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold flex items-center gap-2 mb-5">
          <Shield className="w-5 h-5 text-amber-400" />
          Audit Trail (Hash-Chained)
        </h2>

        <div className="space-y-2">
          {auditEntries.map((entry, i) => (
            <div
              key={i}
              className="flex items-center gap-4 p-3 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--color-border)] text-xs"
            >
              <Clock className="w-3 h-3 text-[var(--color-text-muted)] shrink-0" />
              <span className="text-[var(--color-text-muted)] w-20 shrink-0">{entry.time}</span>
              <span className="font-medium w-36 shrink-0">{entry.actor}</span>
              <span className="font-mono text-[var(--color-accent)] w-40 shrink-0">{entry.action}</span>
              <span className="text-[var(--color-text-secondary)] truncate">{entry.entity}</span>
            </div>
          ))}
        </div>

        <p className="text-[10px] text-[var(--color-text-muted)] mt-3">
          Every prediction stores model version, feature snapshot, output, drivers, viewers,
          and actions — hash-chained for tamper evidence (FR-19).
        </p>
      </div>
    </div>
  );
}
