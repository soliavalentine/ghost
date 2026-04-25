"use client";
import { VariantScore } from "@/lib/types";

const LABELS: Record<string, string> = {
  actual: "Your Name",
  white_coded: "White-Coded Variant",
  black_coded: "Black-Coded Variant",
};

const STYLES: Record<string, { border: string; labelColor: string; bar: string; scoreColor: string }> = {
  white_coded: {
    border: "border-sky-900/40",
    labelColor: "text-sky-700",
    bar: "#38bdf8",
    scoreColor: "text-sky-400",
  },
  black_coded: {
    border: "border-amber-900/40",
    labelColor: "text-amber-700",
    bar: "#f59e0b",
    scoreColor: "text-amber-500",
  },
  neutral: {
    border: "border-zinc-800",
    labelColor: "text-zinc-500",
    bar: "#71717a",
    scoreColor: "text-white",
  },
};

function ScoreRow({
  label,
  score,
  barColor,
  note,
  scoreColor,
}: {
  label: string;
  score: number;
  barColor: string;
  note?: string;
  scoreColor?: string;
}) {
  return (
    <div>
      <div className="flex justify-between items-baseline mb-1.5">
        <span className="text-xs font-mono text-zinc-400">{label}</span>
        <span className={`text-sm font-mono font-bold ${scoreColor ?? "text-white"}`}>
          {Math.round(score)}
        </span>
      </div>
      <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${score}%`, backgroundColor: barColor }}
        />
      </div>
      {note && (
        <div className="text-xs text-zinc-700 font-mono mt-1">{note}</div>
      )}
    </div>
  );
}

export default function ScoreCard({ variant }: { variant: VariantScore }) {
  const styles =
    STYLES[variant.name_coding] ?? STYLES[variant.variant_label] ?? STYLES.neutral;
  const label = LABELS[variant.variant_label] ?? variant.variant_label;

  return (
    <div className={`rounded-xl border bg-zinc-950 p-5 ${styles.border}`}>
      <div className="mb-5">
        <div
          className={`text-xs font-mono uppercase tracking-widest mb-1.5 ${styles.labelColor}`}
        >
          {label}
        </div>
        <div className="text-base font-mono font-semibold text-white leading-tight">
          {variant.variant_name}
        </div>
      </div>

      <div className="space-y-4">
        <ScoreRow
          label="Keyword Match"
          score={variant.keyword_score}
          barColor="#3f3f46"
          note="identical across variants"
        />
        <ScoreRow
          label="ATS Compatibility"
          score={variant.ats_compatibility_score}
          barColor="#3f3f46"
          note="identical across variants"
        />
        <ScoreRow
          label="Simulated Callback"
          score={variant.simulated_callback_score}
          barColor={styles.bar}
          scoreColor={styles.scoreColor}
          note="calibrated to B&M 2004 rates"
        />
      </div>

      {variant.proxy_signals_detected.length > 0 && (
        <div className="mt-5 pt-4 border-t border-zinc-800/60">
          <div className="text-xs font-mono text-zinc-600 uppercase tracking-wider mb-2">
            Proxy Signals ({variant.proxy_signals_detected.length})
          </div>
          <ul className="space-y-1.5">
            {variant.proxy_signals_detected.slice(0, 3).map((s, i) => (
              <li key={i} className="text-xs text-zinc-500 leading-relaxed">
                ↳{" "}
                {s.length > 110 ? s.slice(0, 110) + "…" : s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
