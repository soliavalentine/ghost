"use client";
import { useEffect, useState } from "react";
import { AuditResponse } from "@/lib/types";
import BiasGapCard from "./BiasGapCard";
import GhostReport from "./GhostReport";
import ScoreCard from "./ScoreCard";

type Props = {
  result: AuditResponse | null;
  loading: boolean;
  error: string | null;
};

function EmptyState() {
  return (
    <div className="flex items-center justify-center h-72">
      <div className="text-center space-y-2">
        <div className="text-zinc-700 font-mono text-sm">
          Upload a resume and paste a job description to begin.
        </div>
        <div className="text-zinc-800 font-mono text-xs">
          Three variants. One gap. All grounded in peer-reviewed research.
        </div>
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="flex items-center justify-center h-72">
      <div className="text-center space-y-3">
        <div className="font-mono text-sm text-zinc-400 animate-pulse">
          Running audit pipeline…
        </div>
        <div className="space-y-1">
          {[
            "Parsing resume PDF",
            "Running ATS emulator",
            "Detecting bias signals",
            "Computing name variants",
            "Generating gap explanation",
          ].map((step) => (
            <div key={step} className="text-xs font-mono text-zinc-700">
              {step}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ResultsPanel({ result, loading, error }: Props) {
  const [showGap, setShowGap] = useState(false);

  useEffect(() => {
    if (result) {
      setShowGap(false);
      const t = setTimeout(() => setShowGap(true), 300);
      return () => clearTimeout(t);
    } else {
      setShowGap(false);
    }
  }, [result]);

  if (loading) return <LoadingState />;

  if (error) {
    return (
      <div className="flex items-center justify-center h-72">
        <div className="border border-red-900/60 rounded-xl p-5 text-red-500 font-mono text-sm max-w-lg leading-relaxed">
          {error}
        </div>
      </div>
    );
  }

  if (!result) return <EmptyState />;

  const proxySignalCount = result.black_coded.proxy_signals_detected.length;

  return (
    <div>
      {/* Scorecards render immediately */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <ScoreCard variant={result.actual} />
        <ScoreCard variant={result.white_coded} />
        <ScoreCard variant={result.black_coded} />
      </div>

      {/* Gap + Ghost Report animate in after 300ms stagger */}
      <div
        className="transition-all duration-500 ease-out"
        style={{
          opacity: showGap ? 1 : 0,
          transform: showGap ? "translateY(0)" : "translateY(16px)",
        }}
      >
        <BiasGapCard gap={result.bias_gap} proxySignalCount={proxySignalCount} />
        <GhostReport report={result.ghost_report} />

        {result.methodology_note && (
          <div className="mt-6 text-xs font-mono text-zinc-700 leading-relaxed border-t border-zinc-800/60 pt-4">
            {result.methodology_note}
          </div>
        )}
      </div>
    </div>
  );
}
