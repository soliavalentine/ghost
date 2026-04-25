"use client";
import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Company = {
  company: string;
  sector: string;
  white_callback_rate: number;
  black_callback_rate: number;
  gap_pct: number;
  source: string;
  data_type: string;
};

type MapData = {
  companies: Company[];
  citations: Array<{
    citation: string;
    title: string;
    key_finding: string;
    methodology: string;
  }>;
  methodology_note: string;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function gapColor(gap: number): string {
  if (gap > 25) return "#ef4444";
  if (gap > 15) return "#f97316";
  if (gap > 8) return "#eab308";
  return "#22c55e";
}

export default function DisparityMap() {
  const [data, setData] = useState<MapData | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/disparity-map`)
      .then((r) => r.json())
      .then(setData)
      .catch(() => {});
  }, []);

  if (!data) return null;

  const avgRow = data.companies.find((c) => c.company === "Fortune 500 Average");

  const chartData = [...data.companies]
    .filter((c) => c.company !== "Fortune 500 Average")
    .sort((a, b) => b.gap_pct - a.gap_pct)
    .map((c) => ({
      name: c.company.length > 26 ? c.company.slice(0, 26) + "…" : c.company,
      gap: c.gap_pct,
      sector: c.sector,
    }));

  return (
    <div className="border-t border-zinc-800/60 pt-10">
      <div className="flex items-baseline justify-between mb-1">
        <h2 className="text-xs font-mono uppercase tracking-widest text-zinc-400">
          Collective Disparity Map
        </h2>
        <span className="text-xs font-mono text-zinc-700">
          Kline, Rose &amp; Walters (2022) · Fortune 500 audit study
        </span>
      </div>
      <p className="text-xs font-mono text-zinc-600 mb-8">
        Callback rate gap (%) between white-coded and Black-coded applicants — sorted by disparity
      </p>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{ top: 0, right: 80, left: 210, bottom: 0 }}
          barSize={10}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#1c1c1c"
            horizontal={false}
          />
          <XAxis
            type="number"
            stroke="#2a2a2a"
            tick={{ fill: "#525252", fontFamily: "monospace", fontSize: 11 }}
            tickFormatter={(v) => `${v}%`}
            domain={[0, 50]}
          />
          <YAxis
            type="category"
            dataKey="name"
            stroke="none"
            tick={{ fill: "#737373", fontFamily: "monospace", fontSize: 11 }}
            width={205}
          />
          <Tooltip
            cursor={{ fill: "rgba(255,255,255,0.02)" }}
            contentStyle={{
              backgroundColor: "#111",
              border: "1px solid #222",
              fontFamily: "monospace",
              fontSize: 11,
              color: "#ccc",
            }}
            formatter={(value: number, _name: string, props) => [
              `${value.toFixed(1)}% gap · ${props.payload?.sector}`,
              "Callback gap",
            ]}
          />
          {avgRow && (
            <ReferenceLine
              x={avgRow.gap_pct}
              stroke="#3f3f46"
              strokeDasharray="4 4"
              label={{
                value: `F500 avg ${avgRow.gap_pct}%`,
                fill: "#52525b",
                fontFamily: "monospace",
                fontSize: 10,
                position: "right",
              }}
            />
          )}
          <Bar dataKey="gap" isAnimationActive={true} animationDuration={600}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={gapColor(entry.gap)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex gap-6 mt-4 mb-8">
        {[
          { color: "#ef4444", label: "> 25% gap" },
          { color: "#f97316", label: "15–25%" },
          { color: "#eab308", label: "8–15%" },
          { color: "#22c55e", label: "< 8%" },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div
              className="w-2.5 h-2.5 rounded-sm"
              style={{ backgroundColor: color }}
            />
            <span className="text-xs font-mono text-zinc-600">{label}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-8">
        {/* Research basis */}
        <div>
          <div className="text-xs font-mono text-zinc-600 uppercase tracking-wider mb-3">
            Research Basis
          </div>
          <div className="space-y-4">
            {data.citations.map((c, i) => (
              <div key={i}>
                <div className="text-xs font-mono text-zinc-400">
                  {c.citation}
                </div>
                <div className="text-xs text-zinc-600 mt-0.5 leading-relaxed">
                  {c.key_finding}
                </div>
                <div className="text-xs text-zinc-700 mt-0.5 italic">
                  {c.methodology}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Community submissions */}
        <div>
          <div className="text-xs font-mono text-zinc-600 uppercase tracking-wider mb-3">
            Community Submissions
          </div>
          <div className="border border-dashed border-zinc-800 rounded-lg p-5">
            <div className="text-xs font-mono text-zinc-700 leading-relaxed">
              No community data yet.
            </div>
            <div className="text-xs font-mono text-zinc-800 mt-2 leading-relaxed">
              Every audit you run anonymously contributes a data point to this
              map. Results are aggregated by company and role, never attributed
              to individuals.
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 text-xs font-mono text-zinc-800 leading-relaxed">
        {data.methodology_note}
      </div>
    </div>
  );
}
