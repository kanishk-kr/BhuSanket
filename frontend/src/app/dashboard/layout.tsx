"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileSearch,
  Map,
  ListChecks,
  Shield,
  Bell,
  ChevronLeft,
  ChevronRight,
  Activity,
  Landmark,
  LogOut,
  User,
} from "lucide-react";

const navigation = [
  { name: "Command Center", href: "/dashboard", icon: LayoutDashboard },
  { name: "Project Intelligence", href: "/dashboard/projects", icon: FileSearch },
  { name: "GIS Map View", href: "/dashboard/gis", icon: Map },
  { name: "Interventions", href: "/dashboard/interventions", icon: ListChecks },
  { name: "Governance", href: "/dashboard/governance", icon: Shield },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`${
          collapsed ? "w-20" : "w-72"
        } flex flex-col border-r border-[var(--color-border)] bg-[var(--color-primary)] transition-all duration-300 ease-in-out`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-6 border-b border-[var(--color-border)]">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shrink-0">
            <Landmark className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <div className="animate-fade-in">
              <h1 className="text-lg font-bold tracking-tight text-[var(--color-text-primary)]">
                BhuSanket
              </h1>
              <p className="text-[10px] text-[var(--color-text-muted)] tracking-wider uppercase">
                Land Intelligence
              </p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`nav-item flex items-center gap-3 text-sm font-medium ${
                  isActive ? "active" : ""
                }`}
                title={collapsed ? item.name : undefined}
              >
                <item.icon className="w-5 h-5 shrink-0" />
                {!collapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Bottom Controls */}
        <div className="p-3 border-t border-[var(--color-border)] space-y-2">
          {/* Alerts */}
          <Link
            href="/dashboard/alerts"
            className="nav-item flex items-center gap-3 text-sm"
          >
            <div className="relative">
              <Bell className="w-5 h-5 shrink-0" />
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-500 text-[9px] font-bold text-white flex items-center justify-center">
                4
              </span>
            </div>
            {!collapsed && <span>Alerts</span>}
          </Link>

          {/* User */}
          <div className="nav-item flex items-center gap-3 text-sm opacity-70">
            <User className="w-5 h-5 shrink-0" />
            {!collapsed && (
              <div className="truncate">
                <p className="text-xs font-medium">Dr. Priya Sharma</p>
                <p className="text-[10px] text-[var(--color-text-muted)]">
                  District Collector, Jaipur
                </p>
              </div>
            )}
          </div>

          {/* Collapse Toggle */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center py-2 rounded-lg hover:bg-[rgba(59,130,246,0.08)] text-[var(--color-text-muted)] transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Top Bar */}
        <header className="sticky top-0 z-30 flex items-center justify-between px-8 py-4 border-b border-[var(--color-border)] bg-[rgba(255,255,255,0.85)] backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <Activity className="w-4 h-4 text-green-400" />
            <span className="text-xs text-[var(--color-text-muted)]">
              System Active • Last sync: 2 min ago • Data sources: 6/6 healthy
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs font-mono text-[var(--color-text-muted)]">
              {new Date().toLocaleDateString("en-IN", {
                weekday: "short",
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </span>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
