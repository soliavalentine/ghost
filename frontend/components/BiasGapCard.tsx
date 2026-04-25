"use client";
import { BiasGap } from "@/lib/types";

type Props = {
  gap: BiasGap;
  proxySignalCount?: number;
};

export default function BiasGapCard({ gap, proxySignalCount = 0 }: Props) {
  const proxyPenalty = Math.min(proxySignalCount * 2.5, 15);
  const industryAvg = 24;

  return (
    <div className="rounded-xl border border-red-950 bg-zinc-950 p-8 mb-6">
      {/* Gap reveal — full width, large */}
      <div className="mb-2">
        <div className="text-xs font-mono text-red-800 uppercase tracking-widest mb-3">
          The Gap
        </div>
        <div className="text-8xl font-mono font-bold text-red-500 leading-none tabular-nums">
          {gap.gap_score.toFixed(1)}
        </div>
        <div className="text-base font-mono text-zinc-400 mt-3">
          points lower under a Black-coded name
        </div>
        <div className="text-sm font-mono text-zinc-600 mt-1">
          {gap.gap_percentage.toFixed(1)}% simulated callback score reduction
        </div>
      </div>

      {/* Calibration context — research anchor */}
      <div className="mt-5 p-4 border border-zinc-800/60 rounded-lg bg-zinc-900/40">
        <p className="text-xs font-mono text-zinc-500 leading-relaxed">
          Calibrated to Kline et al. (2022): Black applicants received{" "}
          <span className="text-zinc-300">24% fewer callbacks</span> on average
          at Fortune 500 companies. Industry average gap:{" "}
          <span className="text-zinc-300">{industryAvg}%</span>. Your resume
          gap:{" "}
          <span
            className={
              gap.gap_percentage > industryAvg
                ? "text-red-400"
                : "text-zinc-300"
            }
          >
            {gap.gap_percentage.toFixed(1)}%
          </span>
          {proxySignalCount > 0 && (
            <>
              . Proxy signals detected on this resume shifted the baseline by{" "}
              <span className="text-zinc-300">{proxyPenalty.toFixed(1)} points</span>.
            </>
          )}
        </p>
        <p className="text-xs font-mono text-zinc-700 mt-2">
          {gap.research_grounding}
        </p>
      </div>

      {/* Explanation */}
      <div className="border-t border-zinc-800/60 pt-5 mt-5 mb-4">
        <p className="text-sm text-zinc-300 leading-relaxed">{gap.explanation}</p>
      </div>

      {/* Driving mechanisms */}
      {gap.driving_signals.length > 0 && (
        <div className="mb-5">
          <div className="text-xs font-mono text-zinc-600 uppercase tracking-wider mb-2">
            Driving Mechanisms
          </div>
          <div className="space-y-1.5">
            {gap.driving_signals.map((s, i) => (
              <div key={i} className="text-xs font-mono text-zinc-400">
                → {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System accountability */}
      <div className="border-t border-zinc-800/60 pt-4 mb-5">
        <p className="text-xs font-mono text-zinc-600 italic">
          {gap.system_accountability}
        </p>
      </div>

      {/* Bridge line into Ghost Report */}
      <div className="border-t border-zinc-800/60 pt-5">
        <p className="text-sm font-mono text-zinc-400">
          This is what your resume looks like to a biased system.{" "}
          <span className="text-white">Here&apos;s what you can do about it.</span>
        </p>
      </div>
    </div>
  );
}
