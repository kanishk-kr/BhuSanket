"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  TrendingUp,
  ChevronDown,
  BarChart3,
  MapPin,
} from "lucide-react";
import { mockProjects } from "@/lib/mock-data";

function RiskBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const cls =
    score >= 0.8 ? "critical" : score >= 0.6 ? "red" : score >= 0.4 ? "amber" : "green";
  return <span className={`risk-badge ${cls}`}>{pct}%</span>;
}

function MomentumBadge({ cls, value }: { cls: string; value: number }) {
  const icon =
    cls === "accelerating" ? (
      <ArrowUpRight className="w-3 h-3" />
    ) : cls === "rising" ? (
      <TrendingUp className="w-3 h-3" />
    ) : (
      <Minus className="w-3 h-3" />
    );

  const color =
    cls === "accelerating"
      ? "text-red-400 bg-red-500/10"
      : cls === "rising"
      ? "text-amber-400 bg-amber-500/10"
      : "text-green-400 bg-green-500/10";

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${color}`}>
      {icon}
      {value > 0 ? "+" : ""}{value.toFixed(1)}
    </span>
  );
}

function ConfidenceDot({ value }: { value: number }) {
  const color = value >= 0.8 ? "bg-green-400" : value >= 0.6 ? "bg-amber-400" : "bg-red-400";
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-2 h-2 rounded-full ${color}`} />
      <span className="text-xs">{Math.round(value * 100)}%</span>
    </div>
  );
}

export default function ProjectsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"risk" | "name" | "momentum">("risk");

  const projects = mockProjects.projects
    .filter(
      (p) =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.district?.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === "risk") return (b.current_risk_score ?? 0) - (a.current_risk_score ?? 0);
      if (sortBy === "momentum") return (b.risk_momentum ?? 0) - (a.risk_momentum ?? 0);
      return a.name.localeCompare(b.name);
    });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Project Intelligence</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            {mockProjects.total} projects monitored • {projects.length} shown
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
          <input
            type="text"
            placeholder="Search projects, codes, districts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[var(--color-surface-elevated)] border border-[var(--color-border)] text-sm placeholder:text-[var(--color-text-muted)] focus:border-[var(--color-accent)] focus:outline-none transition-colors"
          />
        </div>
        <div className="flex items-center gap-2">
          {(["risk", "name", "momentum"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSortBy(s)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                sortBy === s
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-[var(--color-surface-elevated)] text-[var(--color-text-secondary)] hover:bg-[rgba(59,130,246,0.08)]"
              }`}
            >
              {s === "risk" ? "Risk ↓" : s === "momentum" ? "Momentum ↓" : "Name ↑"}
            </button>
          ))}
        </div>
      </div>

      {/* Project Table */}
      <div className="glass-card overflow-hidden">
        <table className="data-table">
          <thead>
            <tr>
              <th>Project</th>
              <th>State / District</th>
              <th>Risk</th>
              <th>Momentum</th>
              <th>Land Acquired</th>
              <th>Construction Ready</th>
              <th>Model Conf.</th>
              <th>Data Conf.</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((proj, i) => (
              <tr
                key={proj.id}
                className="cursor-pointer animate-fade-in"
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <td>
                  <Link href={`/dashboard/projects/${proj.id}`} className="block">
                    <p className="font-medium text-sm truncate max-w-[240px]">{proj.name}</p>
                    <p className="text-[10px] font-mono text-[var(--color-text-muted)]">{proj.code}</p>
                  </Link>
                </td>
                <td>
                  <div className="flex items-center gap-1.5 text-xs text-[var(--color-text-secondary)]">
                    <MapPin className="w-3 h-3" />
                    {proj.district}, {proj.state}
                  </div>
                </td>
                <td><RiskBadge score={proj.current_risk_score!} /></td>
                <td>
                  <MomentumBadge cls={proj.risk_momentum_class!} value={proj.risk_momentum!} />
                </td>
                <td>
                  <div className="w-24">
                    <div className="flex justify-between text-[10px] mb-1">
                      <span>{proj.land_acquired_pct}%</span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-bar-fill bg-blue-500"
                        style={{ width: `${proj.land_acquired_pct}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td>
                  <div className="w-24">
                    <div className="flex justify-between text-[10px] mb-1">
                      <span>{proj.construction_enabling_pct}%</span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-bar-fill bg-emerald-500"
                        style={{ width: `${proj.construction_enabling_pct}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td><ConfidenceDot value={proj.model_confidence!} /></td>
                <td><ConfidenceDot value={proj.data_confidence!} /></td>
                <td>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase ${
                      proj.status === "delayed"
                        ? "bg-red-500/15 text-red-400"
                        : proj.status === "active"
                        ? "bg-green-500/15 text-green-400"
                        : "bg-gray-500/15 text-gray-400"
                    }`}
                  >
                    {proj.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
