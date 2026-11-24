"use client";

import React, { useState } from "react";
import { MessageSquare, Files, Award, Sparkles, Terminal } from "lucide-react";
import ChatInterface from "./components/ChatInterface";
import DocumentManager from "./components/DocumentManager";
import EvaluationDashboard from "./components/EvaluationDashboard";
import CitationInspector, { CitationData } from "./components/CitationInspector";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"chat" | "docs" | "eval">("chat");
  const [selectedCitation, setSelectedCitation] = useState<CitationData | null>(null);

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab("chat")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            activeTab === "chat"
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
              : "text-slate-400 hover:text-white hover:bg-slate-900"
          }`}
        >
          <MessageSquare className="h-4 w-4" />
          <span>Interactive Token Streaming RAG</span>
        </button>

        <button
          onClick={() => setActiveTab("docs")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            activeTab === "docs"
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
              : "text-slate-400 hover:text-white hover:bg-slate-900"
          }`}
        >
          <Files className="h-4 w-4" />
          <span>Document Ingestion & pgvector HNSW</span>
        </button>

        <button
          onClick={() => setActiveTab("eval")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            activeTab === "eval"
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30"
              : "text-slate-400 hover:text-white hover:bg-slate-900"
          }`}
        >
          <Award className="h-4 w-4" />
          <span>Ragas Quantitative Evaluation Suite</span>
        </button>
      </div>

      {/* Main Tab Panels */}
      {activeTab === "chat" && (
        <ChatInterface onSelectCitation={(cit) => setSelectedCitation(cit)} />
      )}

      {activeTab === "docs" && <DocumentManager />}

      {activeTab === "eval" && <EvaluationDashboard />}

      {/* Slide-over Citation Inspector Drawer */}
      <CitationInspector
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
}
