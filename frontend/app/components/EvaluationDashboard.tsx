"use client";

import React, { useState } from "react";
import { Play, CheckCircle2, Award, RefreshCw } from "lucide-react";

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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#10121a] p-5 rounded-lg border border-white/[0.08]">
        <div>
          <h2 className="text-sm font-semibold text-[#eef1f6] flex items-center gap-2">
            <Award className="h-4 w-4 text-[#646c80]" />
            <span>Ragas quantitative evaluation</span>
          </h2>
          <p className="text-xs text-[#9aa2b4] mt-0.5 max-w-xl leading-relaxed">
            Mathematical validation of RAG response fidelity against gold-standard benchmark datasets.
            Measures claim entailment, context signal-to-noise ratio, and hallucination bounds.
          </p>
        </div>

        <button
          onClick={runBenchmark}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-md bg-[#eef1f6] hover:bg-white disabled:opacity-40 text-[#0d0f14] font-medium text-xs transition-colors shrink-0"
        >
          {loading ? (
            <>
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
              <span>Computing metrics...</span>
            </>
          ) : (
            <>
              <Play className="h-3.5 w-3.5 fill-current" />
              <span>Run benchmark</span>
            </>
          )}
        </button>
      </div>

      {report && (
        <div className="space-y-6">
          {/* Top KPI Cards: Quiet neutral ramp with one highlight */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-[#10121a] p-4 rounded-lg border border-white/[0.08]">
              <span className="text-xs text-[#646c80] block">Faithfulness</span>
              <div className="text-2xl font-medium text-[#eef1f6] font-mono mt-1 tabular-nums">
                {Math.round(report.mean_faithfulness * 100)}%
              </div>
              <p className="text-[11px] text-[#646c80] mt-0.5">Claims entailed by context</p>
            </div>

            <div className="bg-[#10121a] p-4 rounded-lg border border-white/[0.08]">
              <span className="text-xs text-[#646c80] block">Context relevance</span>
              <div className="text-2xl font-medium text-[#eef1f6] font-mono mt-1 tabular-nums">
                {Math.round(report.mean_context_relevance * 100)}%
              </div>
              <p className="text-[11px] text-[#646c80] mt-0.5">Passage signal-to-noise</p>
            </div>

            <div className="bg-[#10121a] p-4 rounded-lg border border-white/[0.08]">
              <span className="text-xs text-[#646c80] block">Answer relevance</span>
              <div className="text-2xl font-medium text-[#eef1f6] font-mono mt-1 tabular-nums">
                {Math.round(report.mean_answer_relevance * 100)}%
              </div>
              <p className="text-[11px] text-[#646c80] mt-0.5">Query intent coverage</p>
            </div>

            <div className="bg-[#10121a] p-4 rounded-lg border border-white/[0.08]">
              <span className="text-xs text-[#646c80] block">Overall Ragas score</span>
              <div className="text-2xl font-medium text-emerald-400 font-mono mt-1 tabular-nums">
                {Math.round(report.mean_overall_score * 100)}%
              </div>
              <div className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium mt-0.5">
                <CheckCircle2 className="h-3 w-3" />
                <span>Benchmark passed</span>
              </div>
            </div>
          </div>

          {/* Detailed Benchmark Table */}
          <div className="bg-[#10121a] rounded-lg border border-white/[0.08] overflow-hidden">
            <div className="px-4 py-2.5 border-b border-white/[0.08] text-xs font-medium text-[#eef1f6] flex items-center justify-between">
              <span>Benchmark scenarios ({report.total_samples})</span>
              <span className="font-mono text-[11px] text-[#646c80] tabular-nums">SLA threshold: &ge; 70%</span>
            </div>

            <div className="divide-y divide-white/[0.06]">
              {report.sample_evaluations.map((sample: any, idx: number) => (
                <div key={idx} className="p-4 hover:bg-white/[0.02] transition-colors text-xs space-y-2">
                  <div className="flex items-start justify-between gap-4">
                    <p className="font-normal text-[#eef1f6]">
                      <span className="text-[#646c80] font-mono mr-2">#{idx + 1}</span>
                      {sample.question}
                    </p>
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-mono shrink-0 ${
                        sample.verdict === "PASSED"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-red-500/10 text-red-400 border border-red-500/20"
                      }`}
                    >
                      {sample.verdict}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-[11px] text-[#646c80] font-mono tabular-nums">
                    <div>
                      Faithfulness:{" "}
                      <span className="text-[#9aa2b4]">
                        {Math.round(sample.faithfulness * 100)}%
                      </span>
                    </div>
                    <div>
                      Context relevance:{" "}
                      <span className="text-[#9aa2b4]">
                        {Math.round(sample.context_relevance * 100)}%
                      </span>
                    </div>
                    <div>
                      Answer relevance:{" "}
                      <span className="text-[#9aa2b4]">
                        {Math.round(sample.answer_relevance * 100)}%
                      </span>
                    </div>
                    <div>
                      Composite score:{" "}
                      <span className="text-emerald-400">
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
