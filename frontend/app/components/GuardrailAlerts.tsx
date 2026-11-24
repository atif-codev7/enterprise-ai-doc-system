"use client";

import React from "react";
import { ShieldAlert, CheckCircle } from "lucide-react";

interface GuardrailAlertsProps {
  guardrail: {
    is_safe: boolean;
    risk_score: number;
    violated_rules: string[];
    sanitization_applied: boolean;
    flagged_snippet?: string;
  } | null;
}

export default function GuardrailAlerts({ guardrail }: GuardrailAlertsProps) {
  if (!guardrail) return null;

  if (guardrail.is_safe) {
    return (
      <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#13161f] border border-white/[0.08] text-[#9aa2b4] text-xs">
        <CheckCircle className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
        <span className="font-mono text-[11px] tabular-nums">
          Guardrail verified safe &middot; Risk score: {Math.round(guardrail.risk_score * 100)}%
        </span>
      </div>
    );
  }

  return (
    <div className="p-3.5 rounded-lg bg-[#1a1215] border border-red-500/30 text-[#eef1f6] text-xs space-y-2.5">
      <div className="flex items-center gap-2 text-red-400 font-medium">
        <ShieldAlert className="h-4 w-4 shrink-0" />
        <span>Security intervention: adversarial prompt injection intercepted</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
        <div className="bg-[#13161f] p-2.5 rounded border border-white/[0.06]">
          <span className="text-[#646c80] block text-[10px]">Threat probability</span>
          <span className="font-mono font-medium text-red-400 tabular-nums">
            {Math.round(guardrail.risk_score * 100)}% confidence
          </span>
        </div>

        <div className="bg-[#13161f] p-2.5 rounded border border-white/[0.06]">
          <span className="text-[#646c80] block text-[10px]">Policy enforcement</span>
          <span className="text-[#9aa2b4]">
            Execution terminated at guardrail node
          </span>
        </div>
      </div>

      {guardrail.violated_rules.length > 0 && (
        <div className="pt-1">
          <span className="text-[#646c80] block text-[10px] mb-1">Triggered rules</span>
          <div className="flex flex-wrap gap-1">
            {guardrail.violated_rules.map((rule, idx) => (
              <span
                key={idx}
                className="px-1.5 py-0.5 rounded bg-white/[0.05] text-[#9aa2b4] text-[10px] font-mono border border-white/[0.08]"
              >
                {rule}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
