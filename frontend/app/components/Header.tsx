"use client";

import React, { useEffect, useState } from "react";
import { ShieldCheck, Database, FileText } from "lucide-react";

export default function Header() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth({ status: "offline", service: "DocIntel System" }));
  }, []);

  return (
    <header className="border-b border-white/[0.08] bg-[#0d0f14]/90 backdrop-blur px-6 py-3.5 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {/* Flat architectural glyph mark */}
          <div className="h-8 w-8 rounded bg-[#1a1e2a] border border-white/[0.1] flex items-center justify-center text-[#eef1f6]">
            <FileText className="h-4 w-4 text-[#9aa2b4]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold tracking-tight text-[#eef1f6]">
                Enterprise Document Intelligence
              </span>
              <span className="text-[11px] font-mono px-1.5 py-0.2 rounded bg-white/[0.05] text-[#9aa2b4] border border-white/[0.08]">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-[#646c80] mt-0.5">
              Archival document retrieval and deterministic ledger verification
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#13161f] border border-white/[0.08] text-[#9aa2b4]">
            <Database className="h-3.5 w-3.5 text-[#646c80]" />
            <span className="font-mono text-[11px]">HNSW (m=16, ef=64)</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#13161f] border border-white/[0.08] text-[#9aa2b4]">
            <ShieldCheck className="h-3.5 w-3.5 text-[#646c80]" />
            <span className="text-[11px]">Guardrails active</span>
          </div>

          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#13161f] border border-white/[0.08]">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                health?.status === "healthy" ? "bg-emerald-500" : "bg-amber-500"
              }`}
            />
            <span className="text-[#9aa2b4] font-mono text-[11px] tabular-nums">
              {health?.status === "healthy"
                ? `${health.vector_store_chunks} chunks indexed`
                : "Connecting..."}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
