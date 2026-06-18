"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Scan } from "@/lib/types";
import { RiskBadge } from "@/components/risk-badge";

function PromptCell({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false);
  const isLong = text.length > 80;

  return (
    <div className="max-w-sm">
      <p
        className={`text-gray-400 text-xs whitespace-pre-wrap break-words ${
          !expanded && isLong ? "line-clamp-2" : ""
        }`}
      >
        {text}
      </p>
      {isLong && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="mt-1 text-xs text-blue-400 hover:text-blue-300"
        >
          {expanded ? "Show less" : "Show more"}
        </button>
      )}
    </div>
  );
}

export default function ScansPage() {
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.scans.list().then(setScans).finally(() => setLoading(false));
  }, []);

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-white">Scans</h1>
        <p className="mt-1 text-sm text-gray-400">
          {loading ? "Loading…" : `${scans.length} scans`}
        </p>
      </div>

      <div className="rounded-lg border border-gray-800 bg-gray-900 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-left">
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">
                Risk
              </th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">
                Score
              </th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">
                Prompt
              </th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">
                Detections
              </th>
              <th className="px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">
                Date
              </th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {loading && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && scans.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No scans yet.
                </td>
              </tr>
            )}
            {scans.map((scan) => (
              <tr
                key={scan.id}
                className="hover:bg-gray-800/40 transition-colors align-top"
              >
                <td className="px-4 py-3">
                  <RiskBadge level={scan.risk_level} />
                </td>
                <td className="px-4 py-3 font-mono text-white">
                  {scan.risk_score.toFixed(1)}
                </td>
                <td className="px-4 py-3">
                  <PromptCell text={scan.text} />
                </td>
                <td className="px-4 py-3 text-gray-400 max-w-xs">
                  {scan.detections.length > 0 ? (
                    scan.detections
                      .map((d) => d.attack_type.replace(/_/g, " "))
                      .join(", ")
                  ) : (
                    <span className="text-gray-600">None</span>
                  )}
                </td>
                <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                  {new Date(scan.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/scans/${scan.id}`}
                    className="text-xs text-blue-400 hover:text-blue-300"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
