"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Scan } from "@/lib/types";
import { ScanForm } from "@/components/scan-form";
import { RiskBadge } from "@/components/risk-badge";
import { StatsCard } from "@/components/stats-card";
import { RiskDistributionChart } from "@/components/risk-distribution-chart";

export default function HomePage() {
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.scans.list(100).then(setScans).finally(() => setLoading(false));
  }, []);

  const distribution = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
  for (const scan of scans) {
    const lvl = scan.risk_level;
    if (lvl in distribution) distribution[lvl as keyof typeof distribution]++;
  }

  const highOrCritical = distribution.HIGH + distribution.CRITICAL;
  const avgScore =
    scans.length > 0
      ? (scans.reduce((s, x) => s + x.risk_score, 0) / scans.length).toFixed(1)
      : "—";

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-400">
          Prompt injection and LLM threat detection
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatsCard label="Total Scans" value={loading ? "—" : scans.length} />
        <StatsCard label="High / Critical" value={loading ? "—" : highOrCritical} />
        <StatsCard label="Critical" value={loading ? "—" : distribution.CRITICAL} />
        <StatsCard label="Avg Risk Score" value={loading ? "—" : avgScore} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-5">
          <h2 className="mb-4 text-sm font-medium text-white">New Scan</h2>
          <ScanForm />
        </div>

        <div className="rounded-lg border border-gray-800 bg-gray-900 p-5">
          <h2 className="mb-4 text-sm font-medium text-white">Risk Distribution</h2>
          {!loading && <RiskDistributionChart distribution={distribution} />}
          {loading && (
            <div className="h-[180px] flex items-center justify-center text-sm text-gray-600">
              Loading…
            </div>
          )}
        </div>
      </div>

      <div className="rounded-lg border border-gray-800 bg-gray-900">
        <div className="px-5 py-4 border-b border-gray-800">
          <h2 className="text-sm font-medium text-white">Recent Scans</h2>
        </div>
        <div className="divide-y divide-gray-800">
          {loading && (
            <p className="px-5 py-4 text-sm text-gray-500">Loading…</p>
          )}
          {!loading && scans.length === 0 && (
            <p className="px-5 py-4 text-sm text-gray-500">
              No scans yet. Use the form above to run your first scan.
            </p>
          )}
          {scans.slice(0, 10).map((scan) => (
            <div key={scan.id} className="flex items-center gap-4 px-5 py-3">
              <RiskBadge level={scan.risk_level} />
              <span className="text-sm text-white font-mono w-10">
                {scan.risk_score.toFixed(1)}
              </span>
              <span className="text-xs text-gray-500 flex-1 truncate">
                {scan.detections.length > 0
                  ? scan.detections
                      .map((d) => d.attack_type.replace(/_/g, " "))
                      .join(", ")
                  : "No threats detected"}
              </span>
              <span className="text-xs text-gray-600 shrink-0">
                {new Date(scan.created_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
