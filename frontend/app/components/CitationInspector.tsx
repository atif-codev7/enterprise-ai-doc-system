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
    <div className="fixed inset-y-0 right-0 w-full md:w-96 bg-slate-900 border-l border-slate-800 shadow-2xl z-50 p-6 flex flex-col animate-in slide-in-from-right duration-200">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="h-6 w-6 rounded bg-indigo-500/20 text-indigo-400 font-bold flex items-center justify-center text-xs border border-indigo-500/30">
            #{citation.citation_id}
          </span>
          <h3 className="font-semibold text-slate-100 text-sm">Citation Source Inspector</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="py-4 space-y-4 flex-1 overflow-y-auto">
        <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 space-y-2">
          <div className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Document Title</div>
          <div className="text-sm font-medium text-white flex items-center gap-1.5">
            <BookOpen className="h-4 w-4 text-indigo-400 shrink-0" />
            <span className="truncate">{citation.document_title}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Page Reference</div>
            <div className="text-lg font-bold text-white flex items-center gap-1 mt-0.5">
              <Bookmark className="h-4 w-4 text-cyan-400" />
              <span>Page {citation.page_number}</span>
            </div>
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <div className="text-xs text-slate-400">Cosine Similarity</div>
            <div className="text-lg font-bold text-emerald-400 flex items-center gap-1 mt-0.5">
              <CheckCircle2 className="h-4 w-4" />
              <span>{scorePct}%</span>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold uppercase tracking-wider">Grounding Passage Excerpt</span>
            <span className="font-mono text-[10px] text-slate-500">ID: {citation.chunk_id.slice(0, 8)}...</span>
          </div>
          <div className="bg-slate-950 p-4 rounded-lg border border-indigo-500/20 text-xs leading-relaxed text-slate-200 font-serif border-l-2 border-l-indigo-500">
            "{citation.snippet}"
          </div>
        </div>

        <div className="bg-slate-800/40 p-3 rounded-lg border border-slate-800 text-xs text-slate-400 space-y-1">
          <div className="font-medium text-slate-300 flex items-center gap-1">
            <Layers className="h-3.5 w-3.5 text-indigo-400" />
            <span>HNSW Vector Guarantee</span>
          </div>
          <p className="text-[11px] leading-normal">
            Retrieved via PostgreSQL pgvector HNSW index with <code className="text-indigo-300">vector_cosine_ops</code> at search threshold <code className="text-indigo-300">ef_search=40</code>.
          </p>
        </div>
      </div>
    </div>
  );
}
