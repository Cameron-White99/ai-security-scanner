import type { RiskLevel } from "@/lib/types";

const styles: Record<RiskLevel, string> = {
  LOW: "bg-green-500/10 text-green-400 ring-green-500/20",
  MEDIUM: "bg-yellow-500/10 text-yellow-400 ring-yellow-500/20",
  HIGH: "bg-orange-500/10 text-orange-400 ring-orange-500/20",
  CRITICAL: "bg-red-500/10 text-red-400 ring-red-500/20",
};

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${styles[level] ?? styles.LOW}`}
    >
      {level}
    </span>
  );
}
