"use client";

import React from "react";
import { X, BookOpen, Layers, CheckCircle2, Bookmark } from "lucide-react";

export interface CitationData {
  citation_id: number;
  document_id: string;
  document_title: string;
  chunk_id: string;
  page_number: number;
  snippet: string;
  relevance_score: number;
}

interface CitationInspectorProps {
  citation: CitationData | null;
  onClose: () => void;
}

export default function CitationInspector({ citation, onClose }: CitationInspectorProps) {
  if (!citation) return null;

  const scorePct = Math.round(citation.relevance_score * 100);

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-96 bg-[#10121a] border-l border-white/[0.08] shadow-2xl z-50 p-5 flex flex-col">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs px-1.5 py-0.5 rounded bg-white/[0.06] text-[#9aa2b4] border border-white/[0.08]">
            &sect; Doc {citation.citation_id}
          </span>
          <h3 className="font-medium text-[#eef1f6] text-xs">Source passage inspector</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded text-[#646c80] hover:text-[#eef1f6] hover:bg-white/[0.05] transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="py-4 space-y-4 flex-1 overflow-y-auto">
        <div className="bg-[#13161f] p-3 rounded-lg border border-white/[0.08] space-y-1">
          <div className="text-[11px] text-[#646c80]">Document title</div>
          <div className="text-xs font-medium text-[#eef1f6] flex items-center gap-1.5">
            <BookOpen className="h-3.5 w-3.5 text-[#646c80] shrink-0" />
            <span className="truncate">{citation.document_title}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2.5">
          <div className="bg-[#13161f] p-3 rounded-lg border border-white/[0.08]">
            <div className="text-[11px] text-[#646c80]">Page reference</div>
            <div className="text-sm font-semibold text-[#eef1f6] flex items-center gap-1.5 mt-0.5">
              <Bookmark className="h-3.5 w-3.5 text-[#646c80]" />
              <span className="font-mono tabular-nums">Page {citation.page_number}</span>
            </div>
          </div>

          <div className="bg-[#13161f] p-3 rounded-lg border border-white/[0.08]">
            <div className="text-[11px] text-[#646c80]">Cosine similarity</div>
            <div className="text-sm font-semibold text-[#eef1f6] flex items-center gap-1.5 mt-0.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
              <span className="font-mono tabular-nums">{scorePct}%</span>
            </div>
          </div>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-[11px] text-[#646c80]">
            <span>Grounded excerpt</span>
            <span className="font-mono text-[10px]">ID: {citation.chunk_id.slice(0, 8)}</span>
          </div>
          <div className="bg-[#13161f] p-3.5 rounded-lg border border-white/[0.08] text-xs leading-relaxed text-[#9aa2b4] font-mono">
            &ldquo;{citation.snippet}&rdquo;
          </div>
        </div>

        <div className="bg-[#13161f] p-3 rounded-lg border border-white/[0.06] text-[11px] text-[#646c80] space-y-1">
          <div className="font-medium text-[#9aa2b4] flex items-center gap-1.5">
            <Layers className="h-3 w-3 text-[#646c80]" />
            <span>HNSW vector indexing</span>
          </div>
          <p className="leading-normal">
            Retrieved via PostgreSQL pgvector HNSW index with <code className="text-[#9aa2b4]">vector_cosine_ops</code> at search threshold <code className="text-[#9aa2b4]">ef_search=40</code>
          </p>
        </div>
      </div>
    </div>
  );
}
