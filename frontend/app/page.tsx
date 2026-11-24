"use client";

import React, { useState } from "react";
import { MessageSquare, Files, Award } from "lucide-react";
import ChatInterface from "./components/ChatInterface";
import DocumentManager from "./components/DocumentManager";
import EvaluationDashboard from "./components/EvaluationDashboard";
import CitationInspector, { CitationData } from "./components/CitationInspector";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"chat" | "docs" | "eval">("chat");
  const [selectedCitation, setSelectedCitation] = useState<CitationData | null>(null);

  return (
    <div className="space-y-6">
      {/* Tab Navigation: Quiet neutral surface with hairline indicator */}
      <div className="flex items-center gap-1 border-b border-white/[0.08] pb-2 text-xs">
        <button
          onClick={() => setActiveTab("chat")}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "chat"
              ? "bg-[#1a1e2a] text-[#eef1f6] border border-white/[0.12]"
              : "text-[#9aa2b4] hover:text-[#eef1f6] hover:bg-white/[0.04]"
          }`}
        >
          <MessageSquare className="h-3.5 w-3.5 text-[#646c80]" />
          <span>Interactive retrieval & audit</span>
        </button>

        <button
          onClick={() => setActiveTab("docs")}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "docs"
              ? "bg-[#1a1e2a] text-[#eef1f6] border border-white/[0.12]"
              : "text-[#9aa2b4] hover:text-[#eef1f6] hover:bg-white/[0.04]"
          }`}
        >
          <Files className="h-3.5 w-3.5 text-[#646c80]" />
          <span>Document corpus & indexing</span>
        </button>

        <button
          onClick={() => setActiveTab("eval")}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md font-medium transition-colors ${
            activeTab === "eval"
              ? "bg-[#1a1e2a] text-[#eef1f6] border border-white/[0.12]"
              : "text-[#9aa2b4] hover:text-[#eef1f6] hover:bg-white/[0.04]"
          }`}
        >
          <Award className="h-3.5 w-3.5 text-[#646c80]" />
          <span>Ragas quantitative evaluation</span>
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
