"use client";

import React, { useState } from "react";
import { Terminal, ChevronDown, ChevronRight, CheckCircle, Clock } from "lucide-react";

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
    <div className="mt-3.5 border border-white/[0.08] bg-[#0d0f14] rounded-md overflow-hidden">
      <div className="px-3.5 py-2 bg-[#13161f] border-b border-white/[0.08] flex items-center justify-between text-xs text-[#9aa2b4]">
        <div className="flex items-center gap-2">
          <Terminal className="h-3.5 w-3.5 text-[#646c80]" />
          <span className="font-medium text-[#eef1f6]">LangGraph tool execution traces ({traces.length})</span>
        </div>
        <span className="text-[11px] font-mono px-1.5 py-0.2 rounded bg-white/[0.04] text-[#9aa2b4] border border-white/[0.06]">
          Pydantic validated
        </span>
      </div>

      <div className="divide-y divide-white/[0.06]">
        {traces.map((trace, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div key={idx} className="text-xs">
              <button
                onClick={() => setOpenIndex(isOpen ? null : idx)}
                className="w-full px-3.5 py-2 flex items-center justify-between text-left hover:bg-white/[0.03] transition-colors"
              >
                <div className="flex items-center gap-2 truncate">
                  {isOpen ? (
                    <ChevronDown className="h-3 w-3 text-[#646c80] shrink-0" />
                  ) : (
                    <ChevronRight className="h-3 w-3 text-[#646c80] shrink-0" />
                  )}
                  <span className="font-mono text-[11px] text-[#eef1f6]">{trace.tool_name}</span>
                  <span className="text-[#646c80]">&vert;</span>
                  <span className="text-[#9aa2b4] font-mono text-[11px] truncate">
                    {JSON.stringify(trace.input_parameters)}
                  </span>
                </div>

                <div className="flex items-center gap-2.5 shrink-0">
                  <span className="flex items-center gap-1 text-emerald-500 text-[11px] font-mono">
                    <CheckCircle className="h-3 w-3" />
                    {trace.status}
                  </span>
                  <span className="flex items-center gap-1 text-[#646c80] text-[11px] font-mono tabular-nums">
                    <Clock className="h-3 w-3" />
                    {trace.execution_time_ms}ms
                  </span>
                </div>
              </button>

              {isOpen && (
                <div className="px-4 py-3 bg-[#0a0c10] font-mono text-[11px] text-[#9aa2b4] border-t border-white/[0.06] space-y-2.5">
                  <div>
                    <span className="text-[#646c80]">Input payload:</span>
                    <pre className="mt-1 p-2 bg-[#10121a] rounded text-[#eef1f6] border border-white/[0.06] overflow-x-auto">
                      {JSON.stringify(trace.input_parameters, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <span className="text-[#646c80]">Tool output (PayGuard ACID ledger):</span>
                    <pre className="mt-1 p-2 bg-[#10121a] rounded text-[#9aa2b4] border border-white/[0.06] overflow-x-auto">
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
