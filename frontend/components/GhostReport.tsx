"use client";
import { GhostReport as GhostReportType } from "@/lib/types";

export default function GhostReport({ report }: { report: GhostReportType }) {
  const hasSignals = report.detected_signals.length > 0;
  const hasRecommendations = report.recommendations.length > 0;

  if (!hasSignals && !hasRecommendations) return null;

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-6 mt-6">
      <div className="text-xs font-mono text-zinc-500 uppercase tracking-widest mb-6">
        Ghost Report
      </div>

      {/* DETECTED SIGNALS */}
      {hasSignals && (
        <div className="mb-8">
          <div className="text-xs font-mono text-zinc-600 uppercase tracking-wider mb-4">
            Detected Signals
          </div>
          <div className="space-y-4">
            {report.detected_signals.map((signal, i) => (
              <div key={i} className="flex gap-3 items-start">
                <span
                  className={`text-xs font-mono px-2 py-0.5 rounded border whitespace-nowrap mt-0.5 shrink-0 ${
                    signal.classification === "load-bearing"
                      ? "border-amber-800/60 text-amber-600 bg-amber-950/20"
                      : "border-zinc-700 text-zinc-500 bg-zinc-900"
                  }`}
                >
                  {signal.classification}
                </span>
                <div>
                  <p className="text-sm text-zinc-300 leading-relaxed">
                    {signal.text}
                  </p>
                  {signal.mechanism && (
                    <p className="text-xs text-zinc-600 mt-1 leading-relaxed">
                      {signal.mechanism}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* BRIDGE LINE */}
      <div className="border-t border-zinc-800/60 pt-6 mb-6">
        <p className="text-base text-white font-medium leading-relaxed">
          {report.bridge_line}
        </p>
      </div>

      {/* REDUCE BIAS SURFACE AREA */}
      {hasRecommendations && (
        <div>
          <div className="text-xs font-mono text-zinc-600 uppercase tracking-wider mb-4">
            Reduce Bias Surface Area
          </div>
          <div className="space-y-3">
            {report.recommendations.map((rec, i) => (
              <div key={i} className="flex gap-3 items-start">
                <span className="text-zinc-700 font-mono text-sm shrink-0 mt-0.5">
                  →
                </span>
                <p className="text-sm text-zinc-400 leading-relaxed">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
