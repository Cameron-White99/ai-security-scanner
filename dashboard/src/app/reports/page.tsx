"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Report } from "@/lib/types";
import { RiskDistributionChart } from "@/components/risk-distribution-chart";

function toLocalDatetimeString(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}`
  );
}

function todayMinus(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return toLocalDatetimeString(d);
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [selected, setSelected] = useState<Report | null>(null);
  const [genError, setGenError] = useState<string | null>(null);

  useEffect(() => {
    setFromDate(todayMinus(7));
    setToDate(toLocalDatetimeString(new Date()));
    api.reports.list().then(setReports).finally(() => setLoading(false));
  }, []);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    setGenerating(true);
    setGenError(null);
    try {
      const report = await api.reports.create(
        new Date(fromDate).toISOString(),
        new Date(toDate).toISOString(),
      );
      setReports((prev) => [report, ...prev]);
      setSelected(report);
    } catch (err) {
      setGenError(err instanceof Error ? err.message : "Failed to generate report");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-white">Reports</h1>
        <p className="mt-1 text-sm text-gray-400">
          Aggregate security reports over a time window
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Sidebar: generate + list */}
        <div className="space-y-4">
          <div className="rounded-lg border border-gray-800 bg-gray-900 p-5">
            <h2 className="mb-4 text-sm font-medium text-white">
              Generate Report
            </h2>
            <form onSubmit={handleGenerate} className="space-y-3">
              <div>
                <label className="text-xs text-gray-500">From</label>
                <input
                  type="datetime-local"
                  value={fromDate}
                  onChange={(e) => setFromDate(e.target.value)}
                  required
                  className="mt-1 w-full rounded border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-xs text-gray-500">To</label>
                <input
                  type="datetime-local"
                  value={toDate}
                  onChange={(e) => setToDate(e.target.value)}
                  required
                  className="mt-1 w-full rounded border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
              {genError && <p className="text-xs text-red-400">{genError}</p>}
              <button
                type="submit"
                disabled={generating}
                className="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50 transition-colors"
              >
                {generating ? "Generating…" : "Generate"}
              </button>
            </form>
          </div>

          <div className="rounded-lg border border-gray-800 bg-gray-900 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-800 text-xs font-medium text-gray-500 uppercase tracking-wide">
              Past Reports
            </div>
            {loading && (
              <p className="px-4 py-4 text-sm text-gray-500">Loading…</p>
            )}
            {!loading && reports.length === 0 && (
              <p className="px-4 py-4 text-sm text-gray-500">
                No reports yet.
              </p>
            )}
            <div className="divide-y divide-gray-800">
              {reports.map((r) => (
                <button
                  key={r.id}
                  onClick={() => setSelected(r)}
                  className={`w-full text-left px-4 py-3 transition-colors hover:bg-gray-800/50 ${
                    selected?.id === r.id ? "bg-gray-800/50" : ""
                  }`}
                >
                  <p className="text-xs text-white">
                    {new Date(r.generated_at).toLocaleDateString()}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {r.total_scans} scan{r.total_scans !== 1 ? "s" : ""}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Detail panel */}
        <div className="lg:col-span-2">
          {!selected ? (
            <div className="rounded-lg border border-gray-800 bg-gray-900 p-10 text-center text-sm text-gray-500">
              Select or generate a report to view details.
            </div>
          ) : (
            <div className="space-y-5">
              {/* Summary */}
              <div className="rounded-lg border border-gray-800 bg-gray-900 p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-medium text-white">Summary</h2>
                  <span className="text-xs text-gray-500">
                    {new Date(selected.generated_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm text-gray-400 leading-relaxed">
                  {selected.summary}
                </p>
                <div className="grid grid-cols-3 gap-4 pt-3 border-t border-gray-800 text-sm">
                  <div>
                    <p className="text-xs text-gray-500">Total Scans</p>
                    <p className="mt-1 text-lg font-semibold text-white">
                      {selected.total_scans}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">From</p>
                    <p className="mt-1 text-xs text-gray-300">
                      {new Date(selected.from_date).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">To</p>
                    <p className="mt-1 text-xs text-gray-300">
                      {new Date(selected.to_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Risk distribution chart */}
              <div className="rounded-lg border border-gray-800 bg-gray-900 p-5">
                <h3 className="mb-4 text-sm font-medium text-white">
                  Risk Distribution
                </h3>
                <RiskDistributionChart distribution={selected.risk_distribution} />
              </div>

              {/* Attack type breakdown */}
              {Object.keys(selected.attack_type_breakdown).length > 0 && (
                <div className="rounded-lg border border-gray-800 bg-gray-900 p-5">
                  <h3 className="mb-4 text-sm font-medium text-white">
                    Attack Types
                  </h3>
                  <div className="space-y-3">
                    {(() => {
                      const maxCount = Math.max(
                        ...Object.values(selected.attack_type_breakdown),
                      );
                      return Object.entries(selected.attack_type_breakdown)
                        .sort(([, a], [, b]) => b - a)
                        .map(([type, count]) => (
                          <div key={type} className="flex items-center gap-3">
                            <span className="text-xs text-gray-300 capitalize w-36 shrink-0">
                              {type.replace(/_/g, " ")}
                            </span>
                            <div className="flex-1 bg-gray-800 rounded-full h-1.5">
                              <div
                                className="bg-blue-500 h-1.5 rounded-full transition-all"
                                style={{
                                  width:
                                    maxCount > 0
                                      ? `${(count / maxCount) * 100}%`
                                      : "0%",
                                }}
                              />
                            </div>
                            <span className="text-xs text-gray-500 w-6 text-right">
                              {count}
                            </span>
                          </div>
                        ));
                    })()}
                  </div>
                </div>
              )}

              {/* Mitigations */}
              {Object.keys(selected.mitigations).length > 0 && (
                <div className="rounded-lg border border-gray-800 bg-gray-900 p-5 space-y-4">
                  <h3 className="text-sm font-medium text-white">
                    Recommended Mitigations
                  </h3>
                  {Object.entries(selected.mitigations).map(([type, text]) => (
                    <div key={type}>
                      <p className="text-xs font-medium text-gray-300 capitalize">
                        {type.replace(/_/g, " ")}
                      </p>
                      <p className="mt-1 text-xs text-gray-500 leading-relaxed">
                        {text}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
