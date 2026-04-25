"use client";
import { useState } from "react";
import DisparityMap from "@/components/DisparityMap";
import InputPanel from "@/components/InputPanel";
import ResultsPanel from "@/components/ResultsPanel";
import { AuditResponse } from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [result, setResult] = useState<AuditResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showResearch, setShowResearch] = useState(false);

  const handleAudit = async (fd: FormData) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/audit`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? "Audit failed");
      }
      setResult(await res.json());
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "An unexpected error occurred."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      <header className="border-b border-zinc-800/60 px-8 py-5">
        <div className="max-w-7xl mx-auto flex items-baseline gap-4">
          <h1 className="text-xl font-mono font-bold tracking-widest text-white">
            GHOST
          </h1>
          <span className="text-zinc-600 text-xs font-mono">
            hiring bias audit · grounded in Bertrand &amp; Mullainathan (2004)
          </span>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-8 py-6">
        {/* Framing line */}
        <p className="text-sm font-mono text-zinc-500 mb-8 border-b border-zinc-800/40 pb-6">
          Ghost doesn&apos;t audit you. It audits the system —{" "}
          <span className="text-zinc-400">
            using your resume as the probe.
          </span>
        </p>

        <div className="grid grid-cols-[380px_1fr] gap-10 items-start">
          <InputPanel onSubmit={handleAudit} loading={loading} />
          <ResultsPanel result={result} loading={loading} error={error} />
        </div>

        {/* Research Basis — collapsible, out of main flow */}
        <div className="mt-14 border border-zinc-800/60 rounded-xl overflow-hidden">
          <button
            onClick={() => setShowResearch((v) => !v)}
            className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-zinc-900/60 transition-colors"
          >
            <div className="flex items-baseline gap-4">
              <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">
                Research Basis
              </span>
              <span className="text-xs font-mono text-zinc-700">
                Kline, Rose &amp; Walters (2022) Fortune 500 Audit · Bertrand
                &amp; Mullainathan (2004)
              </span>
            </div>
            <span className="text-zinc-600 font-mono text-lg leading-none">
              {showResearch ? "−" : "+"}
            </span>
          </button>
          {showResearch && (
            <div className="border-t border-zinc-800/60">
              <DisparityMap />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
