"use client";

import React, { useEffect, useState } from "react";
import { ShieldCheck, Database, Cpu, Activity, Sparkles } from "lucide-react";

export default function Header() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth({ status: "offline", service: "DocIntel System" }));
  }, []);

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 py-4 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Cpu className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">
                Enterprise AI Document Intelligence
              </h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Next.js &rarr; FastAPI &rarr; pgvector (HNSW) &rarr; LangGraph &rarr; Ragas Evaluation
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-800/80 border border-slate-700/60 text-slate-300">
            <Database className="h-3.5 w-3.5 text-cyan-400" />
            <span>HNSW Index (m=16, ef=64)</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-800/80 border border-slate-700/60 text-slate-300">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>Guardrails Active</span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-800/80 border border-slate-700/60">
            <span
              className={`h-2 w-2 rounded-full ${
                health?.status === "healthy" ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
              }`}
            />
            <span className="text-slate-300 font-mono">
              {health?.status === "healthy"
                ? `${health.vector_store_chunks} Chunks Indexed`
                : "Connecting API..."}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
