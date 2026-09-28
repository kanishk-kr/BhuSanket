"use client";

import { useState } from "react";
import {
  Bell,
  AlertTriangle,
  Clock,
  Gavel,
  Database,
  CheckCircle,
  Pause,
  Eye,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { mockCommandCenter } from "@/lib/mock-data";

const allAlerts = [
  ...mockCommandCenter.top_alerts,
  {
    id: "a5", project_id: "p5", alert_type: "risk.threshold_crossed", title: "Rising risk: Chennai Outer Ring Road Extension",
    description: "Risk crossed 60% threshold. Momentum +5.7 pts/wk. 12 blocking parcels.", severity: "medium",
    priority_index: 65.8, owner_role: "project_manager", state: "open", created_at: "2026-09-27T09:00:00Z",
  },
  {
    id: "a6", project_id: "p6", alert_type: "data.staleness", title: "Stale data: Lucknow Metro legal feed",
    description: "Court data last synced 12 days ago. Legal data confidence 43%.", severity: "low",
    priority_index: 42.1, owner_role: "data_steward", state: "acknowledged", created_at: "2026-09-26T16:00:00Z",
  },
  {
    id: "a7", project_id: "p3", alert_type: "silence.detected", title: "Administrative silence: Ahmedabad Ring Road survey stage",
    description: "No updates for 45 days on survey stage. Source healthy.", severity: "medium",
    priority_index: 58.3, owner_role: "field_officer", state: "snoozed", created_at: "2026-09-25T11:00:00Z",
  },
];

const alertTypeIcons: Record<string, typeof AlertTriangle> = {
  "risk.threshold_crossed": AlertTriangle,
  "clock.deadline_risk": Clock,
  "court.stay_detected": Gavel,
  "contradiction.raised": Database,
  "data.staleness": Database,
  "silence.detected": Pause,
};

export default function AlertsPage() {
  const [stateFilter, setStateFilter] = useState<string>("all");

  const filtered = stateFilter === "all"
    ? allAlerts
    : allAlerts.filter((a) => a.state === stateFilter);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Alerts & Notifications</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            {allAlerts.filter((a) => a.state === "open").length} open alerts requiring attention
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {["all", "open", "acknowledged", "snoozed"].map((s) => (
          <button
            key={s}
            onClick={() => setStateFilter(s)}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              stateFilter === s
                ? "bg-[var(--color-accent)] text-white"
                : "glass-card text-[var(--color-text-secondary)]"
            }`}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
            <span className="ml-2 opacity-70">
              ({s === "all" ? allAlerts.length : allAlerts.filter((a) => a.state === s).length})
            </span>
          </button>
        ))}
      </div>

      <div className="space-y-3 stagger-children">
        {filtered.map((alert) => {
          const Icon = alertTypeIcons[alert.alert_type] || AlertTriangle;
          return (
            <div
              key={alert.id}
              className="glass-card p-5 flex items-start gap-4 hover:border-[var(--color-border-active)]"
            >
              <div className={`mt-1 p-2 rounded-lg ${
                alert.severity === "critical" ? "bg-red-500/15" : alert.severity === "high" ? "bg-amber-500/15" : "bg-blue-500/15"
              }`}>
                <Icon className={`w-4 h-4 ${
                  alert.severity === "critical" ? "text-red-400" : alert.severity === "high" ? "text-amber-400" : "text-blue-400"
                }`} />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`clock-badge ${
                    alert.state === "open" ? (alert.severity === "critical" ? "CRITICAL" : "RED") : alert.state === "snoozed" ? "AMBER" : "GREEN"
                  }`}>
                    {alert.state}
                  </span>
                  <span className="text-[10px] text-[var(--color-text-muted)]">
                    Priority: {alert.priority_index?.toFixed(1)}
                  </span>
                  <span className="text-[10px] text-[var(--color-text-muted)]">
                    • {alert.owner_role?.replace("_", " ")}
                  </span>
                </div>
                <p className="text-sm font-medium">{alert.title}</p>
                <p className="text-xs text-[var(--color-text-secondary)] mt-1">{alert.description}</p>
                <p className="text-[10px] text-[var(--color-text-muted)] mt-2">
                  {new Date(alert.created_at).toLocaleString("en-IN")}
                </p>
              </div>

              <div className="flex items-center gap-2">
                {alert.state === "open" && (
                  <>
                    <button className="px-3 py-1.5 rounded-lg bg-[var(--color-accent)] text-white text-[10px] font-medium hover:bg-[var(--color-accent-hover)] transition-colors">
                      Acknowledge
                    </button>
                    <button className="px-3 py-1.5 rounded-lg bg-[var(--color-surface-elevated)] border border-[var(--color-border)] text-[10px] font-medium hover:border-[var(--color-accent)] transition-colors">
                      Snooze
                    </button>
                  </>
                )}
                <Link href={`/dashboard/projects/${alert.project_id}`}>
                  <Eye className="w-4 h-4 text-[var(--color-text-muted)] hover:text-[var(--color-accent)] transition-colors" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
