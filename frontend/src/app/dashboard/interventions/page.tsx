"use client";

import { useState } from "react";
import {
  ListChecks,
  Play,
  CheckCircle,
  Clock,
  User,
  ChevronRight,
  Plus,
  Calculator,
  AlertTriangle,
} from "lucide-react";

const interventionQueue = [
  {
    id: "i1",
    project_name: "NH-48 Jaipur Bypass Extension",
    project_code: "LA-RJ-JAI-0012",
    action: "Verification Camp",
    action_code: "VERIFICATION_CAMP",
    owner_role: "Field Officer",
    assigned_to: "Ramesh Kumar",
    risk_before: 0.82,
    risk_after_modelled: 0.65,
    priority_index: 94.2,
    due_date: "2026-10-15",
    status: "pending",
    blocking_parcels: 10,
  },
  {
    id: "i2",
    project_name: "NH-48 Jaipur Bypass Extension",
    project_code: "LA-RJ-JAI-0012",
    action: "Batch Compensation Processing",
    action_code: "BATCH_COMPENSATION",
    owner_role: "Revenue Officer",
    assigned_to: "Priya Mehta",
    risk_before: 0.82,
    risk_after_modelled: 0.58,
    priority_index: 91.5,
    due_date: "2026-10-20",
    status: "in_progress",
    blocking_parcels: 7,
  },
  {
    id: "i3",
    project_name: "Pune Industrial Corridor Phase 2",
    project_code: "LA-MH-PUN-0034",
    action: "Legal Review",
    action_code: "LEGAL_REVIEW",
    owner_role: "Legal Officer",
    assigned_to: "Adv. Meera Nair",
    risk_before: 0.79,
    risk_after_modelled: 0.62,
    priority_index: 87.3,
    due_date: "2026-10-08",
    status: "pending",
    blocking_parcels: 12,
  },
  {
    id: "i4",
    project_name: "Ahmedabad Ring Road Phase 3",
    project_code: "LA-GJ-AHM-0021",
    action: "R&R Consultation Meeting",
    action_code: "RR_MEETING",
    owner_role: "R&R Officer",
    assigned_to: "Suresh Patel",
    risk_before: 0.74,
    risk_after_modelled: 0.59,
    priority_index: 78.6,
    due_date: "2026-10-12",
    status: "pending",
    blocking_parcels: 5,
  },
  {
    id: "i5",
    project_name: "Bhopal-Indore Expressway",
    project_code: "LA-MP-BHO-0007",
    action: "Revenue Camp",
    action_code: "REVENUE_CAMP",
    owner_role: "Field Officer",
    assigned_to: "Aarti Singh",
    risk_before: 0.45,
    risk_after_modelled: 0.32,
    priority_index: 52.1,
    due_date: "2026-10-25",
    status: "completed",
    blocking_parcels: 2,
  },
];

const statusConfig = {
  pending: { icon: Clock, color: "text-amber-400", bg: "bg-amber-500/15", label: "Pending" },
  in_progress: { icon: Play, color: "text-blue-400", bg: "bg-blue-500/15", label: "In Progress" },
  completed: { icon: CheckCircle, color: "text-green-400", bg: "bg-green-500/15", label: "Completed" },
};

export default function InterventionsPage() {
  const [filter, setFilter] = useState<"all" | "pending" | "in_progress" | "completed">("all");

  const filtered = filter === "all"
    ? interventionQueue
    : interventionQueue.filter((i) => i.status === filter);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Intervention Management</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            Actions, owners, deadlines, outcomes — the intervention queue
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[var(--color-accent)] text-white text-sm font-medium hover:bg-[var(--color-accent-hover)] transition-colors">
          <Plus className="w-4 h-4" />
          New Intervention
        </button>
      </div>

      {/* Status Filters */}
      <div className="flex items-center gap-3">
        {(["all", "pending", "in_progress", "completed"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              filter === s
                ? "bg-[var(--color-accent)] text-white"
                : "glass-card text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            }`}
          >
            {s === "all" ? "All" : s === "in_progress" ? "In Progress" : s.charAt(0).toUpperCase() + s.slice(1)}
            {s !== "all" && (
              <span className="ml-2 text-[10px] opacity-70">
                ({interventionQueue.filter((i) => i.status === s).length})
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Intervention Cards */}
      <div className="space-y-4 stagger-children">
        {filtered.map((intervention) => {
          const statusCfg = statusConfig[intervention.status as keyof typeof statusConfig];
          const riskReduction = intervention.risk_before - intervention.risk_after_modelled;

          return (
            <div
              key={intervention.id}
              className="glass-card p-5 hover:border-[var(--color-border-active)]"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-semibold ${statusCfg.bg} ${statusCfg.color}`}>
                      <statusCfg.icon className="w-3 h-3" />
                      {statusCfg.label}
                    </span>
                    <span className="text-xs font-mono text-[var(--color-text-muted)]">
                      {intervention.project_code}
                    </span>
                    <span className="text-xs text-[var(--color-text-muted)]">
                      Priority: {intervention.priority_index.toFixed(1)}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold mb-1">{intervention.action}</h3>
                  <p className="text-xs text-[var(--color-text-secondary)]">
                    {intervention.project_name}
                  </p>
                </div>

                {/* Risk Impact */}
                <div className="text-right">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-[var(--color-text-muted)]">
                      {Math.round(intervention.risk_before * 100)}%
                    </span>
                    <ChevronRight className="w-3 h-3 text-[var(--color-text-muted)]" />
                    <span className="text-xs font-bold text-emerald-400">
                      {Math.round(intervention.risk_after_modelled * 100)}%
                    </span>
                  </div>
                  <p className="text-[10px] text-emerald-400">
                    ↓ {Math.round(riskReduction * 100)} pts (model-estimated)
                  </p>
                </div>
              </div>

              {/* Details Row */}
              <div className="flex items-center gap-6 mt-4 pt-3 border-t border-[var(--color-border)] text-xs text-[var(--color-text-secondary)]">
                <span className="flex items-center gap-1.5">
                  <User className="w-3 h-3" />
                  {intervention.assigned_to} ({intervention.owner_role})
                </span>
                <span className="flex items-center gap-1.5">
                  <Clock className="w-3 h-3" />
                  Due: {new Date(intervention.due_date).toLocaleDateString("en-IN", { month: "short", day: "numeric" })}
                </span>
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="w-3 h-3" />
                  {intervention.blocking_parcels} blocking parcels
                </span>
                <span className="flex items-center gap-1.5">
                  <Calculator className="w-3 h-3 text-amber-400" />
                  <span className="italic text-[var(--color-text-muted)]">Model simulation, not a guarantee</span>
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
