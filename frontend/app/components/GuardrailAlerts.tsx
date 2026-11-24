"use client";

import React from "react";
import { AlertTriangle, ShieldAlert, CheckCircle, Lock } from "lucide-react";

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
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
        <CheckCircle className="h-3.5 w-3.5 shrink-0" />
        <span>Guardrail Verified Safe (Risk Confidence: {Math.round(guardrail.risk_score * 100)}%)</span>
      </div>
    );
  }

  return (
    <div className="p-4 rounded-lg bg-red-950/40 border border-red-500/40 text-red-200 text-xs space-y-2 animate-in fade-in duration-200">
      <div className="flex items-center gap-2 text-red-400 font-semibold text-sm">
        <ShieldAlert className="h-5 w-5 shrink-0 animate-bounce" />
        <span>Security Intervention: Adversarial Prompt-Injection Blocked</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
        <div className="bg-slate-900/80 p-2.5 rounded border border-red-900/50">
          <span className="text-slate-400 block text-[10px] uppercase font-bold">Threat Risk Score</span>
          <span className="text-base font-mono font-bold text-red-400">
            {Math.round(guardrail.risk_score * 100)}% Risk Probability
          </span>
        </div>

        <div className="bg-slate-900/80 p-2.5 rounded border border-red-900/50">
          <span className="text-slate-400 block text-[10px] uppercase font-bold">Enforcement Action</span>
          <span className="text-sm font-semibold text-amber-300">
            Execution Terminated at Guardrail Node
          </span>
        </div>
      </div>

      {guardrail.violated_rules.length > 0 && (
        <div>
          <span className="text-slate-400 block text-[11px] mb-1">Triggered Security Rules:</span>
          <div className="flex flex-wrap gap-1.5">
            {guardrail.violated_rules.map((rule, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded bg-red-900/60 text-red-200 text-[10px] font-mono border border-red-700/50"
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
