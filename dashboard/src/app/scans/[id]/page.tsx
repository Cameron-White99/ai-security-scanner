"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Scan } from "@/lib/types";
import { RiskBadge } from "@/components/risk-badge";

export default function ScanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [scan, setScan] = useState<Scan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.scans
      .get(id)
      .then(setScan)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-8 text-gray-500 text-sm">
        Loading…
      </main>
    );
  }

  if (error || !scan) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-8 text-red-400 text-sm">
        {error ?? "Scan not found."}
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8 space-y-6">
      <Link
        href="/scans"
        className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
      >
        ← Back to scans
      </Link>

      <div className="rounded-lg border border-gray-800 bg-gray-900 p-5 space-y-4">
        <div className="flex items-center gap-4">
          <RiskBadge level={scan.risk_level} />
          <span className="text-3xl font-bold text-white">
            {scan.risk_score.toFixed(1)}
          </span>
          {scan.llm_fallback_used && (
            <span className="ml-auto text-xs text-gray-500 border border-gray-700 rounded px-2 py-1">
              LLM fallback
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm pt-3 border-t border-gray-800">
          <div>
            <p className="text-xs text-gray-500">Scan ID</p>
            <p className="mt-1 text-gray-300 font-mono text-xs break-all">
              {scan.id}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Date</p>
            <p className="mt-1 text-gray-300">
              {new Date(scan.created_at).toLocaleString()}
            </p>
          </div>
          {scan.source && (
            <div>
              <p className="text-xs text-gray-500">Source</p>
              <p className="mt-1 text-gray-300">{scan.source}</p>
            </div>
          )}
        </div>

        {scan.text && (
          <div className="pt-3 border-t border-gray-800 space-y-1">
            <p className="text-xs text-gray-500">Evaluated prompt</p>
            <p className="text-sm text-gray-300 bg-gray-800 rounded px-3 py-2 whitespace-pre-wrap break-words leading-relaxed">
              {scan.text}
            </p>
          </div>
        )}
      </div>

      {scan.detections.length > 0 ? (
        <div className="space-y-3">
          <h2 className="text-sm font-medium text-white">
            Detections ({scan.detections.length})
          </h2>
          {scan.detections.map((d, i) => (
            <div
              key={i}
              className="rounded-lg border border-gray-800 bg-gray-900 p-4 space-y-2"
            >
              <div className="flex items-start justify-between gap-4">
                <span className="font-medium text-white capitalize">
                  {d.attack_type.replace(/_/g, " ")}
                </span>
                <div className="flex items-center gap-2 text-xs text-gray-500 shrink-0">
                  <span>{d.detection_method}</span>
                  <span>·</span>
                  <span>{(d.confidence * 100).toFixed(0)}% confidence</span>
                  <span>·</span>
                  <RiskBadge level={d.severity} />
                </div>
              </div>
              <p className="text-sm text-gray-400">{d.description}</p>
              {d.matched_pattern && (
                <p className="text-xs font-mono text-gray-500 bg-gray-800 rounded px-3 py-2 break-all">
                  {d.matched_pattern}
                </p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-5 text-sm text-gray-500">
          No threats detected in this scan.
        </div>
      )}
    </main>
  );
}
