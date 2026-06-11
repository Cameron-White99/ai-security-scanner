"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { Scan } from "@/lib/types";
import { RiskBadge } from "./risk-badge";

export function ScanForm() {
  const [text, setText] = useState("");
  const [source, setSource] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Scan | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const scan = await api.scans.create(text, source || undefined);
      setResult(scan);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste text to analyse for prompt injection..."
          rows={5}
          className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none resize-none"
          required
        />
        <div className="flex gap-3">
          <input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="Source (optional)"
            className="flex-1 rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading || !text.trim()}
            className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Scanning…" : "Scan"}
          </button>
        </div>
      </form>

      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}

      {result && (
        <div className="mt-4 rounded-lg border border-gray-700 bg-gray-800/50 p-4 space-y-3">
          <div className="flex items-center gap-3">
            <RiskBadge level={result.risk_level} />
            <span className="text-2xl font-bold text-white">
              {result.risk_score.toFixed(1)}
            </span>
            <span className="text-sm text-gray-400">risk score</span>
            {result.llm_fallback_used && (
              <span className="ml-auto text-xs text-gray-500">
                LLM fallback used
              </span>
            )}
          </div>
          {result.detections.length > 0 ? (
            <div className="space-y-2">
              {result.detections.map((d, i) => (
                <div
                  key={i}
                  className="rounded border border-gray-700 p-3 text-sm"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white capitalize">
                      {d.attack_type.replace(/_/g, " ")}
                    </span>
                    <span className="text-xs text-gray-400">
                      {(d.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  <p className="mt-1 text-gray-400">{d.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">No threats detected.</p>
          )}
        </div>
      )}
    </div>
  );
}
