"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from "recharts";

const COLORS: Record<string, string> = {
  LOW: "#4ade80",
  MEDIUM: "#facc15",
  HIGH: "#fb923c",
  CRITICAL: "#f87171",
};

interface Props {
  distribution: Record<string, number>;
}

export function RiskDistributionChart({ distribution }: Props) {
  const data = ["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((level) => ({
    name: level,
    count: distribution[level] ?? 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 4, right: 4, bottom: 4, left: -20 }}>
        <XAxis
          dataKey="name"
          tick={{ fill: "#9ca3af", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "#9ca3af", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          allowDecimals={false}
        />
        <Tooltip
          contentStyle={{
            background: "#1f2937",
            border: "1px solid #374151",
            borderRadius: 6,
            fontSize: 12,
          }}
          labelStyle={{ color: "#f9fafb" }}
          cursor={{ fill: "rgba(255,255,255,0.04)" }}
        />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
