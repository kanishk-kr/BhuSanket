"use client";

import { use } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  TrendingUp,
  AlertTriangle,
  Clock,
  MapPin,
  FileText,
  ChevronRight,
  Zap,
  Shield,
  BarChart3,
  Activity,
  Scale,
  Users,
} from "lucide-react";
import {
  mockProjects,
  mockClocks,
  mockExplanation,
  mockRiskTimeline,
} from "@/lib/mock-data";

function RiskGauge({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    score >= 0.8
      ? "#EF4444"
      : score >= 0.6
      ? "#F59E0B"
      : score >= 0.4
      ? "#3B82F6"
      : "#10B981";
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score * 0.75 * circumference);

  return (
    <div className="relative w-36 h-36">
      <svg viewBox="0 0 120 120" className="w-full h-full -rotate-[135deg]">
        <circle
          cx="60"
          cy="60"
          r="54"
          fill="none"
          stroke="rgba(148,163,184,0.1)"
          strokeWidth="8"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeLinecap="round"
        />
        <circle
          cx="60"
          cy="60"
          r="54"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
          style={{ filter: `drop-shadow(0 0 8px ${color}40)` }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold" style={{ color }}>
          {pct}%
        </span>
        <span className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">
          Risk
        </span>
      </div>
    </div>
  );
}

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const project = mockProjects.projects.find((p) => p.id === id) || mockProjects.projects[0];
  const explanation = mockExplanation;
  const clocks = mockClocks;

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
        <Link
          href="/dashboard/projects"
          className="flex items-center gap-1 hover:text-[var(--color-accent)] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Projects
        </Link>
        <ChevronRight className="w-3 h-3" />
        <span className="text-[var(--color-text-primary)] font-medium">{project.code}</span>
      </div>

      {/* Project Header */}
      <div className="glass-card p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="font-mono text-xs text-[var(--color-text-muted)]">{project.code}</span>
              <span className={`inline-flex px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase ${
                project.status === "delayed" ? "bg-red-500/15 text-red-400" : "bg-green-500/15 text-green-400"
              }`}>
                {project.status}
              </span>
            </div>
            <h1 className="text-xl font-bold tracking-tight">{project.name}</h1>
            <div className="flex items-center gap-4 mt-2 text-xs text-[var(--color-text-secondary)]">
              <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {project.district}, {project.state}</span>
              <span>•</span>
              <span>{project.sector}</span>
              <span>•</span>
              <span>₹{project.budget} Cr</span>
              <span>•</span>
              <span>{project.total_parcels} parcels</span>
            </div>
          </div>
          <RiskGauge score={project.current_risk_score!} />
        </div>

        {/* Key Metrics Row */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6 pt-6 border-t border-[var(--color-border)]">
          <div>
            <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">Momentum</p>
            <p className={`text-lg font-bold ${project.risk_momentum_class === "accelerating" ? "text-red-400" : project.risk_momentum_class === "rising" ? "text-amber-400" : "text-green-400"}`}>
              {project.risk_momentum! > 0 ? "+" : ""}{project.risk_momentum} pts/wk
            </p>
            <p className="text-[10px] text-[var(--color-text-muted)] capitalize">{project.risk_momentum_class}</p>
          </div>
          <div>
            <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">Land Acquired</p>
            <p className="text-lg font-bold">{project.land_acquired_pct}%</p>
            <div className="progress-bar mt-1"><div className="progress-bar-fill bg-blue-500" style={{ width: `${project.land_acquired_pct}%` }} /></div>
          </div>
          <div>
            <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">Construction-Enabling</p>
            <p className="text-lg font-bold text-emerald-400">{project.construction_enabling_pct}%</p>
            <div className="progress-bar mt-1"><div className="progress-bar-fill bg-emerald-500" style={{ width: `${project.construction_enabling_pct}%` }} /></div>
          </div>
          <div>
            <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">Model Confidence</p>
            <p className="text-lg font-bold">{Math.round(project.model_confidence! * 100)}%</p>
            <p className="text-[10px] text-[var(--color-text-muted)]">{project.model_confidence! >= 0.8 ? "High" : "Medium"}</p>
          </div>
          <div>
            <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider">Data Confidence</p>
            <p className="text-lg font-bold">{Math.round(project.data_confidence! * 100)}%</p>
            <p className="text-[10px] text-[var(--color-text-muted)]">{project.data_confidence! >= 0.7 ? "Acceptable" : "Review needed"}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Statutory Clocks */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-amber-400" />
            Statutory Clocks
          </h2>
          <div className="space-y-3">
            {clocks.map((clock) => (
              <div key={clock.id} className="p-4 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--color-border)]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono text-[var(--color-text-muted)]">
                    Section {clock.section_reference}
                  </span>
                  <span className={`clock-badge ${clock.alert_state}`}>
                    {clock.alert_state}
                  </span>
                </div>
                <p className="text-sm font-medium mb-2">{clock.description}</p>
                <div className="flex items-center justify-between text-xs text-[var(--color-text-secondary)]">
                  <span>{clock.days_remaining} days remaining</span>
                  <span>Risk: {Math.round(clock.deadline_risk * 100)}%</span>
                </div>
                <div className="progress-bar mt-2">
                  <div
                    className={`progress-bar-fill ${
                      clock.alert_state === "CRITICAL" ? "bg-red-500" : clock.alert_state === "RED" ? "bg-red-400" : clock.alert_state === "AMBER" ? "bg-amber-500" : "bg-green-500"
                    }`}
                    style={{ width: `${Math.min(100, clock.deadline_risk * 100)}%` }}
                  />
                </div>
                <div className="flex items-center gap-3 mt-2 text-[10px] text-[var(--color-text-muted)]">
                  <span>Extensions: {clock.extension_count}</span>
                  <span>•</span>
                  <span>Paused days: {clock.total_paused_days}</span>
                  <span>•</span>
                  <span>Consequence: {clock.consequence}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Why? — Evidence-Backed Drivers */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            Why is this project at risk?
          </h2>
          <p className="text-sm text-[var(--color-text-secondary)] mb-4">
            {explanation.summary}
          </p>

          <div className="space-y-3">
            {explanation.drivers.map((driver, i) => (
              <div key={i} className="p-4 rounded-xl bg-[rgba(255,255,255,0.02)] border border-[var(--color-border)]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">{driver.display_name}</span>
                  <div className="flex items-center gap-2">
                    <span className={`clock-badge ${driver.grade === "HIGH" ? "GREEN" : driver.grade === "MEDIUM" ? "AMBER" : "RED"}`}>
                      {driver.grade}
                    </span>
                    <span className="text-xs font-mono text-red-400">
                      +{Math.round(driver.contribution * 100)}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-[var(--color-text-secondary)] mb-2">
                  {driver.description}
                </p>
                {/* Evidence */}
                {driver.evidence.map((ev, j) => (
                  <div key={j} className="flex items-start gap-2 mt-2 p-2 rounded-lg bg-[rgba(59,130,246,0.04)]">
                    <FileText className="w-3 h-3 text-[var(--color-accent)] mt-0.5 shrink-0" />
                    <div>
                      <p className="text-[10px] text-[var(--color-text-muted)]">{ev.source} • {ev.record_type}</p>
                      <p className="text-xs text-[var(--color-text-secondary)]">{ev.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>

          <p className="text-[10px] text-[var(--color-text-muted)] mt-4">
            {explanation.total_evidence_records} evidence records supporting this explanation.
            Click "Show evidence" to view underlying records.
          </p>
        </div>
      </div>

      {/* Risk Timeline */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          Risk Trajectory
        </h2>
        <div className="h-48 flex items-end gap-1">
          {mockRiskTimeline.map((point, i) => {
            const height = point.risk_score * 100;
            const color =
              point.risk_score >= 0.8
                ? "bg-red-500"
                : point.risk_score >= 0.6
                ? "bg-amber-500"
                : point.risk_score >= 0.4
                ? "bg-blue-500"
                : "bg-green-500";
            return (
              <div key={i} className="flex-1 h-full flex flex-col justify-end items-center gap-1 group">
                <span className="text-[10px] text-[var(--color-text-muted)] opacity-0 group-hover:opacity-100 transition-opacity">
                  {Math.round(point.risk_score * 100)}%
                </span>
                <div
                  className={`w-full rounded-t-md ${color} transition-all duration-700 ease-out hover:opacity-80`}
                  style={{ height: `${height}%`, animationDelay: `${i * 0.1}s` }}
                />
                <span className="text-[8px] text-[var(--color-text-muted)] rotate-[-45deg] origin-top-left whitespace-nowrap">
                  {new Date(point.date).toLocaleDateString("en-IN", { month: "short", day: "numeric" })}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
