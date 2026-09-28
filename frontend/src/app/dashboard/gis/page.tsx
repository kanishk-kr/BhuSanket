"use client";

import { useEffect, useRef, useState } from "react";
import { Layers, Filter, MapPin, AlertTriangle, Eye } from "lucide-react";
import { mockProjects } from "@/lib/mock-data";

// Synthetic GIS data points across India
const projectPoints = [
  { id: "p1", name: "NH-48 Jaipur Bypass Extension", lat: 26.9124, lng: 75.7873, risk: 0.82, parcels: 234, blocking: 10 },
  { id: "p2", name: "Pune Industrial Corridor Phase 2", lat: 18.5204, lng: 73.8567, risk: 0.79, parcels: 412, blocking: 15 },
  { id: "p3", name: "Ahmedabad Ring Road Phase 3", lat: 23.0225, lng: 72.5714, risk: 0.74, parcels: 178, blocking: 8 },
  { id: "p4", name: "Bhopal-Indore Expressway", lat: 23.2599, lng: 77.4126, risk: 0.45, parcels: 523, blocking: 3 },
  { id: "p5", name: "Chennai Outer Ring Road", lat: 13.0827, lng: 80.2707, risk: 0.61, parcels: 367, blocking: 12 },
  { id: "p6", name: "Lucknow Metro Extension", lat: 26.8467, lng: 80.9462, risk: 0.38, parcels: 145, blocking: 2 },
  { id: "p7", name: "Hyderabad ORR Extension", lat: 17.385, lng: 78.4867, risk: 0.55, parcels: 289, blocking: 6 },
  { id: "p8", name: "Bengaluru-Mysuru Expressway", lat: 12.9716, lng: 77.5946, risk: 0.68, parcels: 456, blocking: 14 },
  { id: "p9", name: "Patna Ring Road", lat: 25.6093, lng: 85.1376, risk: 0.71, parcels: 312, blocking: 9 },
  { id: "p10", name: "Bhubaneswar-Puri Corridor", lat: 20.2961, lng: 85.8245, risk: 0.43, parcels: 198, blocking: 4 },
];

const layers = [
  { id: "risk", name: "Project Risk", active: true, color: "#EF4444" },
  { id: "blocking", name: "Blocking Parcels", active: false, color: "#F59E0B" },
  { id: "clocks", name: "Clock Threats", active: false, color: "#8B5CF6" },
  { id: "readiness", name: "Workfront Readiness", active: false, color: "#10B981" },
  { id: "legal", name: "Legal Hotspots", active: false, color: "#EC4899" },
  { id: "grievance", name: "Grievance Density", active: false, color: "#06B6D4" },
];

function RiskDot({ risk, size = 20 }: { risk: number; size?: number }) {
  const color =
    risk >= 0.8 ? "#EF4444" : risk >= 0.6 ? "#F59E0B" : risk >= 0.4 ? "#3B82F6" : "#10B981";
  return (
    <div
      className="rounded-full border-2 border-white/20 shadow-lg"
      style={{
        width: size,
        height: size,
        background: `radial-gradient(circle, ${color}CC, ${color}40)`,
        boxShadow: `0 0 ${size}px ${color}60`,
      }}
    />
  );
}

export default function GISPage() {
  const [activeLayers, setActiveLayers] = useState<string[]>(["risk"]);
  const [selectedProject, setSelectedProject] = useState<typeof projectPoints[0] | null>(null);
  const [showLayers, setShowLayers] = useState(true);

  const toggleLayer = (id: string) => {
    setActiveLayers((prev) =>
      prev.includes(id) ? prev.filter((l) => l !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">GIS Intelligence Map</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            Geospatial visualization of land acquisition projects across India
          </p>
        </div>
        <button
          onClick={() => setShowLayers(!showLayers)}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[var(--color-surface-elevated)] border border-[var(--color-border)] text-sm hover:border-[var(--color-accent)] transition-colors"
        >
          <Layers className="w-4 h-4" />
          Layers
        </button>
      </div>

      <div className="flex gap-6">
        {/* Map Container */}
        <div className="flex-1 glass-card overflow-hidden relative" style={{ height: "calc(100vh - 240px)" }}>
          {/* SVG India Map (simplified) */}
          <div className="w-full h-full bg-[#0a0f1e] relative overflow-hidden rounded-2xl">
            {/* Grid lines */}
            <svg className="absolute inset-0 w-full h-full opacity-10">
              {Array.from({ length: 20 }, (_, i) => (
                <line key={`h${i}`} x1="0" y1={`${i * 5}%`} x2="100%" y2={`${i * 5}%`} stroke="#3B82F6" strokeWidth="0.5" />
              ))}
              {Array.from({ length: 20 }, (_, i) => (
                <line key={`v${i}`} x1={`${i * 5}%`} y1="0" x2={`${i * 5}%`} y2="100%" stroke="#3B82F6" strokeWidth="0.5" />
              ))}
            </svg>

            {/* India outline hint */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-[80%] h-[90%] border border-[var(--color-border)] rounded-3xl opacity-20" />
            </div>

            {/* Project Points */}
            {projectPoints.map((point) => {
              // Map lat/lng to percentage positions on the container
              const x = ((point.lng - 68) / (90 - 68)) * 80 + 10; // India lng range ~68-90
              const y = ((35 - point.lat) / (35 - 8)) * 85 + 5; // India lat range ~8-35

              return (
                <button
                  key={point.id}
                  className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
                  style={{ left: `${x}%`, top: `${y}%` }}
                  onClick={() => setSelectedProject(point)}
                >
                  <div className="relative">
                    <RiskDot risk={point.risk} size={point.blocking > 10 ? 28 : 20} />
                    {/* Pulse ring for high risk */}
                    {point.risk >= 0.7 && (
                      <div
                        className="absolute inset-0 rounded-full animate-ping opacity-30"
                        style={{ background: point.risk >= 0.8 ? "#EF4444" : "#F59E0B" }}
                      />
                    )}
                    {/* Tooltip */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-20">
                      <div className="bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg p-3 shadow-2xl whitespace-nowrap">
                        <p className="text-xs font-semibold">{point.name}</p>
                        <div className="flex items-center gap-3 mt-1 text-[10px] text-[var(--color-text-secondary)]">
                          <span>Risk: {Math.round(point.risk * 100)}%</span>
                          <span>•</span>
                          <span>{point.parcels} parcels</span>
                          <span>•</span>
                          <span className="text-red-400">{point.blocking} blocking</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-xl p-3 z-20">
              <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Risk Level</p>
              <div className="space-y-1.5">
                {[
                  { label: "Critical (>80%)", color: "#EF4444" },
                  { label: "High (60-80%)", color: "#F59E0B" },
                  { label: "Medium (40-60%)", color: "#3B82F6" },
                  { label: "Low (<40%)", color: "#10B981" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ background: item.color }} />
                    <span className="text-[10px] text-[var(--color-text-secondary)]">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Selected Project Detail */}
          {selectedProject && (
            <div className="absolute top-4 right-4 w-72 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-xl p-4 z-20 animate-scale-in shadow-2xl">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-sm font-semibold">{selectedProject.name}</h3>
                <button
                  onClick={() => setSelectedProject(null)}
                  className="text-[var(--color-text-muted)] hover:text-white text-xs"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-muted)]">Risk Score</span>
                  <span className={`font-bold ${selectedProject.risk >= 0.7 ? "text-red-400" : "text-amber-400"}`}>
                    {Math.round(selectedProject.risk * 100)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-muted)]">Total Parcels</span>
                  <span>{selectedProject.parcels}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-muted)]">Blocking Parcels</span>
                  <span className="text-red-400 font-semibold">{selectedProject.blocking}</span>
                </div>
              </div>
              <a
                href={`/dashboard/projects/${selectedProject.id}`}
                className="mt-3 flex items-center justify-center gap-1 w-full py-2 rounded-lg bg-[var(--color-accent)] text-white text-xs font-medium hover:bg-[var(--color-accent-hover)] transition-colors"
              >
                <Eye className="w-3 h-3" /> View Details
              </a>
            </div>
          )}
        </div>

        {/* Layer Panel */}
        {showLayers && (
          <div className="w-64 glass-card p-5 animate-slide-in" style={{ height: "calc(100vh - 240px)" }}>
            <h3 className="text-sm font-semibold mb-4">Map Layers</h3>
            <div className="space-y-2">
              {layers.map((layer) => (
                <button
                  key={layer.id}
                  onClick={() => toggleLayer(layer.id)}
                  className={`w-full flex items-center gap-3 p-3 rounded-xl text-sm transition-all ${
                    activeLayers.includes(layer.id)
                      ? "bg-[rgba(59,130,246,0.1)] border border-[var(--color-border-active)]"
                      : "bg-[rgba(255,255,255,0.02)] border border-[var(--color-border)] opacity-60 hover:opacity-100"
                  }`}
                >
                  <div
                    className="w-3 h-3 rounded-sm shrink-0"
                    style={{ background: layer.color }}
                  />
                  <span className="text-xs">{layer.name}</span>
                </button>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-[var(--color-border)]">
              <h4 className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-3">
                Summary
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Total on map</span>
                  <span className="font-medium">{projectPoints.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Critical risk</span>
                  <span className="font-medium text-red-400">
                    {projectPoints.filter((p) => p.risk >= 0.8).length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">With blocking parcels</span>
                  <span className="font-medium text-amber-400">
                    {projectPoints.filter((p) => p.blocking > 5).length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
