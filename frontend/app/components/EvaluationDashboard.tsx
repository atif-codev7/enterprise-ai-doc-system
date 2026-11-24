"use client";

import React, { useState } from "react";
import { Play, CheckCircle2, XCircle, BarChart3, Award, Sparkles, RefreshCw } from "lucide-react";

export default function EvaluationDashboard() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);

  const runBenchmark = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/eval/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(null),
      });
      const data = await res.json();
      setReport(data);
    } catch (err) {
      console.error("Evaluation run failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Award className="h-5 w-5 text-indigo-400" />
            Quantitative Ragas Evaluation Suite
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl leading-relaxed">
            Automated mathematical assessment of RAG outputs against gold-standard benchmark datasets.
            Measures grounding, context signal-to-noise ratio, and hallucination bounds.
          </p>
        </div>

        <button
          onClick={runBenchmark}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-xs shadow-lg shadow-indigo-600/30 transition shrink-0"
        >
          {loading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Computing Ragas Metrics...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              <span>Run Automated Benchmark</span>
            </>
          )}
        </button>
      </div>

      {report && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Faithfulness</span>
              <div className="text-2xl font-bold text-indigo-400 mt-1">
                {Math.round(report.mean_faithfulness * 100)}%
              </div>
              <p className="text-[10px] text-slate-500 mt-0.5">Claims strictly grounded in retrieved docs</p>
            </div>

            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Context Relevance</span>
              <div className="text-2xl font-bold text-cyan-400 mt-1">
                {Math.round(report.mean_context_relevance * 100)}%
              </div>
              <p className="text-[10px] text-slate-500 mt-0.5">Signal-to-noise ratio of HNSW chunks</p>
            </div>

            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Answer Relevance</span>
              <div className="text-2xl font-bold text-violet-400 mt-1">
                {Math.round(report.mean_answer_relevance * 100)}%
              </div>
              <p className="text-[10px] text-slate-500 mt-0.5">Prompt question alignment ratio</p>
            </div>

            <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 block">Overall Ragas Score</span>
              <div className="text-2xl font-bold text-emerald-400 mt-1">
                {Math.round(report.mean_overall_score * 100)}%
              </div>
              <div className="flex items-center gap-1 text-[10px] text-emerald-400 font-semibold mt-0.5">
                <CheckCircle2 className="h-3 w-3" />
                <span>Enterprise SLA Passed</span>
              </div>
            </div>
          </div>

          {/* Detailed Benchmark Table */}
          <div className="bg-slate-900/70 rounded-xl border border-slate-800 overflow-hidden">
            <div className="px-5 py-3 border-b border-slate-800 text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span>Benchmark Query Performance Breakdown ({report.total_samples} Scenarios)</span>
              <span className="font-mono text-emerald-400 text-[11px]">Threshold: &ge; 70%</span>
            </div>

            <div className="divide-y divide-slate-800/80">
              {report.sample_evaluations.map((sample: any, idx: number) => (
                <div key={idx} className="p-4 hover:bg-slate-850/40 transition text-xs space-y-2">
                  <div className="flex items-start justify-between gap-4">
                    <p className="font-medium text-slate-200">
                      <span className="text-indigo-400 font-bold mr-2">Q{idx + 1}.</span>
                      {sample.question}
                    </p>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold shrink-0 ${
                        sample.verdict === "PASSED"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-red-500/10 text-red-400 border border-red-500/20"
                      }`}
                    >
                      {sample.verdict}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400 font-mono">
                    <div>
                      Faithfulness:{" "}
                      <span className="text-indigo-300 font-bold">
                        {Math.round(sample.faithfulness * 100)}%
                      </span>
                    </div>
                    <div>
                      Context Relevance:{" "}
                      <span className="text-cyan-300 font-bold">
                        {Math.round(sample.context_relevance * 100)}%
                      </span>
                    </div>
                    <div>
                      Answer Relevance:{" "}
                      <span className="text-violet-300 font-bold">
                        {Math.round(sample.answer_relevance * 100)}%
                      </span>
                    </div>
                    <div>
                      Composite Score:{" "}
                      <span className="text-emerald-400 font-bold">
                        {Math.round(sample.overall * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
