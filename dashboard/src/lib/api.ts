import type { Scan, Report } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    let detail = body;
    try {
      detail = JSON.parse(body)?.detail ?? body;
    } catch {}
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  scans: {
    list: (limit = 50, offset = 0) =>
      apiFetch<Scan[]>(`/scans/?limit=${limit}&offset=${offset}`),
    get: (id: string) => apiFetch<Scan>(`/scans/${id}`),
    create: (text: string, source?: string) =>
      apiFetch<Scan>("/scans/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, source }),
      }),
  },
  reports: {
    list: (limit = 50, offset = 0) =>
      apiFetch<Report[]>(`/reports/?limit=${limit}&offset=${offset}`),
    get: (id: string) => apiFetch<Report>(`/reports/${id}`),
    create: (from_date: string, to_date: string) =>
      apiFetch<Report>("/reports/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ from_date, to_date }),
      }),
  },
};
