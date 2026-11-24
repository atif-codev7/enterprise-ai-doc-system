"use client";

import React, { useState } from "react";
import { Terminal, ChevronDown, ChevronRight, CheckCircle, Clock, ShieldCheck } from "lucide-react";

export interface ToolTrace {
  tool_name: string;
  input_parameters: any;
  output_result: any;
  execution_time_ms: number;
  status: string;
}

interface ToolExecutionLogProps {
  traces: ToolTrace[];
}

export default function ToolExecutionLog({ traces }: ToolExecutionLogProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  if (!traces || traces.length === 0) return null;

  return (
    <div className="mt-4 border border-slate-800 bg-slate-950/90 rounded-lg overflow-hidden shadow-inner">
      <div className="px-4 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-xs font-semibold text-slate-300">
        <div className="flex items-center gap-2">
          <Terminal className="h-4 w-4 text-amber-400" />
          <span>Deterministic LangGraph Tool Execution Traces ({traces.length})</span>
        </div>
        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
          Strict Pydantic Validated
        </span>
      </div>

      <div className="divide-y divide-slate-800/80">
        {traces.map((trace, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div key={idx} className="text-xs">
              <button
                onClick={() => setOpenIndex(isOpen ? null : idx)}
                className="w-full px-4 py-2 flex items-center justify-between text-left hover:bg-slate-900/50 transition"
              >
                <div className="flex items-center gap-2">
                  {isOpen ? (
                    <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
                  ) : (
                    <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
                  )}
                  <span className="font-mono font-medium text-indigo-400">{trace.tool_name}</span>
                  <span className="text-slate-500">|</span>
                  <span className="text-slate-400">
                    Input: {JSON.stringify(trace.input_parameters)}
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1 text-emerald-400 text-[11px] font-mono">
                    <CheckCircle className="h-3 w-3" />
                    {trace.status}
                  </span>
                  <span className="flex items-center gap-1 text-slate-400 text-[11px] font-mono">
                    <Clock className="h-3 w-3 text-slate-500" />
                    {trace.execution_time_ms}ms
                  </span>
                </div>
              </button>

              {isOpen && (
                <div className="px-6 py-3 bg-slate-950 font-mono text-[11px] text-slate-300 border-t border-slate-900 space-y-2">
                  <div>
                    <span className="text-slate-500 font-bold">Input Payload (Validated):</span>
                    <pre className="mt-1 p-2 bg-slate-900/90 rounded text-emerald-300 overflow-x-auto">
                      {JSON.stringify(trace.input_parameters, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <span className="text-slate-500 font-bold">Tool Output (PayGuard ACID Verified):</span>
                    <pre className="mt-1 p-2 bg-slate-900/90 rounded text-cyan-300 overflow-x-auto">
                      {JSON.stringify(trace.output_result, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
