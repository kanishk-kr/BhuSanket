"use client";

import { useState } from "react";
import {
  AlertTriangle,
  TrendingUp,
  Clock,
  MapPin,
  Gavel,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Shield,
  Zap,
  Eye,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { mockCommandCenter } from "@/lib/mock-data";

function RiskBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const cls =
    score >= 0.8 ? "critical" : score >= 0.6 ? "red" : score >= 0.4 ? "amber" : "green";
  return <span className={`risk-badge ${cls}`}>{pct}%</span>;
}

function MomentumIcon({ cls }: { cls: string }) {
  if (cls === "accelerating") return <ArrowUpRight className="w-4 h-4 text-red-400" />;
  if (cls === "rising") return <TrendingUp className="w-4 h-4 text-amber-400" />;
  return <Minus className="w-4 h-4 text-green-400" />;
}

export default function CommandCenter() {
  const data = mockCommandCenter;

  const statCards = [
    {
      label: "Land Acquired",
      value: `${data.hero_metrics.land_acquired_pct}%`,
      sub: "Unweighted acquisition",
      color: "from-blue-500/20 to-blue-600/5",
      icon: MapPin,
    },
    {
      label: "Construction-Enabling",
      value: `${data.hero_metrics.construction_enabling_pct}%`,
      sub: "Criticality-weighted possession",
      color: "from-emerald-500/20 to-emerald-600/5",
      icon: Zap,
    },
    {
      label: "Critical Parcels Resolved",
      value: `${data.hero_metrics.critical_parcels_resolved_pct}%`,
      sub: `${data.blocking_parcels_count} parcels still blocking`,
      color: "from-amber-500/20 to-amber-600/5",
      icon: Shield,
    },
    {
      label: "Statutory Clocks at Risk",
      value: data.hero_metrics.statutory_clocks_at_risk.toString(),
      sub: "RED or CRITICAL state",
      color: "from-red-500/20 to-red-600/5",
      icon: Clock,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Command Center</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            What needs attention today?
          </p>
        </div>
        <div className="flex items-center gap-6 text-sm">
          <div className="glass-card px-4 py-2 flex items-center gap-2">
            <span className="text-[var(--color-text-muted)]">Projects:</span>
            <span className="font-semibold">{data.total_projects}</span>
          </div>
          <div className="glass-card px-4 py-2 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span className="text-[var(--color-text-muted)]">At Risk:</span>
            <span className="font-semibold text-red-400">{data.at_risk_projects}</span>
          </div>
        </div>
      </div>

      {/* Hero Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 stagger-children">
        {statCards.map((card) => (
          <div
            key={card.label}
            className={`glass-card stat-card p-5 bg-gradient-to-br ${card.color}`}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider font-medium">
                  {card.label}
                </p>
                <p className="text-3xl font-bold mt-2 tracking-tight">{card.value}</p>
                <p className="text-xs text-[var(--color-text-secondary)] mt-1">{card.sub}</p>
              </div>
              <card.icon className="w-5 h-5 text-[var(--color-text-muted)] opacity-50" />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Alerts */}
        <div className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              Priority Alerts
            </h2>
            <Link
              href="/dashboard/alerts"
              className="text-xs text-[var(--color-accent)] hover:underline flex items-center gap-1"
            >
              View all <ChevronRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-3">
            {data.top_alerts.map((alert, i) => (
              <div
                key={alert.id}
                className="flex items-start gap-4 p-4 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--color-border)] hover:border-[var(--color-border-active)] transition-all cursor-pointer"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <div
                  className={`mt-1 w-2 h-2 rounded-full shrink-0 ${
                    alert.severity === "critical"
                      ? "bg-red-500 animate-pulse"
                      : alert.severity === "high"
                      ? "bg-amber-500"
                      : "bg-blue-500"
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`clock-badge ${
                        alert.severity === "critical"
                          ? "CRITICAL"
                          : alert.severity === "high"
                          ? "RED"
                          : "AMBER"
                      }`}
                    >
                      {alert.alert_type.replace(".", " · ")}
                    </span>
                    <span className="text-xs text-[var(--color-text-muted)]">
                      Priority: {alert.priority_index?.toFixed(1)}
                    </span>
                  </div>
                  <p className="text-sm font-medium truncate">{alert.title}</p>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-1 line-clamp-2">
                    {alert.description}
                  </p>
                </div>
                <Eye className="w-4 h-4 text-[var(--color-text-muted)] shrink-0 mt-1" />
              </div>
            ))}
          </div>
        </div>

        {/* Deteriorating Projects */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-5">
            <TrendingUp className="w-5 h-5 text-red-400" />
            Rapidly Deteriorating
          </h2>

          <div className="space-y-4">
            {data.deteriorating_projects.map((proj) => (
              <Link
                key={proj.id}
                href={`/dashboard/projects/${proj.id}`}
                className="block p-4 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--color-border)] hover:border-[var(--color-border-active)] transition-all"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-[var(--color-text-muted)]">
                    {proj.code}
                  </span>
                  <RiskBadge score={proj.current_risk_score!} />
                </div>
                <p className="text-sm font-medium truncate mb-2">{proj.name}</p>
                <div className="flex items-center gap-3 text-xs text-[var(--color-text-secondary)]">
                  <span className="flex items-center gap-1">
                    <MomentumIcon cls={proj.risk_momentum_class!} />
                    {proj.risk_momentum! > 0 ? "+" : ""}
                    {proj.risk_momentum?.toFixed(1)} pts/wk
                  </span>
                  <span>•</span>
                  <span>{proj.district}</span>
                </div>

                {/* Progress Bars */}
                <div className="mt-3 space-y-2">
                  <div>
                    <div className="flex justify-between text-[10px] text-[var(--color-text-muted)] mb-1">
                      <span>Land Acquired</span>
                      <span>{proj.land_acquired_pct}%</span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-bar-fill bg-blue-500"
                        style={{ width: `${proj.land_acquired_pct}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-[10px] text-[var(--color-text-muted)] mb-1">
                      <span>Construction-Enabling</span>
                      <span>{proj.construction_enabling_pct}%</span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-bar-fill bg-emerald-500"
                        style={{ width: `${proj.construction_enabling_pct}%` }}
                      />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row: Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-amber-400">{data.pending_interventions}</p>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">Pending Interventions</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-red-400">{data.data_contradictions}</p>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">Data Contradictions</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-blue-400">
            {(data.hero_metrics.avg_risk_score * 100).toFixed(0)}%
          </p>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">Average Risk Score</p>
        </div>
        <div className="glass-card p-4 text-center">
          <p className="text-2xl font-bold text-emerald-400">6/6</p>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">Data Sources Healthy</p>
        </div>
      </div>
    </div>
  );
}
