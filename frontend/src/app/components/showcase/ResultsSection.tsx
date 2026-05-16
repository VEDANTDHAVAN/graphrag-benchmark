import Link from "next/link";
import { Award, Gauge, Medal, Timer } from "lucide-react";
import { ResultsCharts } from "../charts/ResultsCharts";
import { FinalSummary, PIPELINES, formatNumber, formatPercent, formatRate } from "../../lib/showcase";
import { SectionShell } from "./SectionShell";

export function ResultsSection({ summary, source }: { summary: FinalSummary; source: "api" | "fallback" }) {
  const winners = {
    accuracy: best(summary, "llm_judge_pass_rate", "max"),
    tokens: best(summary, "avg_total_tokens", "min"),
    latency: best(summary, "avg_latency_seconds", "min"),
    overall: bestOverall(summary),
  };
  return (
    <SectionShell id="results" eyebrow="Results" title="Efficiency, cost, and quality in one view" description="The dashboard preserves raw answers and context while the landing page summarizes judge-facing metrics.">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="text-sm text-[var(--text-secondary)]">
          Data source: <span className="font-semibold text-[var(--text-primary)]">{source === "api" ? "Live backend final_summary.json" : "Fallback demo values"}</span>
        </div>
        <Link href="/benchmark" className="inline-flex h-10 items-center rounded-lg bg-blue-600 px-4 text-sm font-semibold text-white hover:bg-blue-700">
          Open full dashboard
        </Link>
      </div>
      <div className="mb-6 overflow-x-auto rounded-xl border border-[var(--border)] bg-[var(--surface)]">
        <table className="w-full min-w-[980px] text-left text-sm">
          <thead className="border-b border-[var(--border)] text-xs uppercase tracking-wide text-[var(--text-secondary)]">
            <tr>
              {["Pipeline", "Badges", "Judge", "BERT F1", "Avg Tokens", "Latency", "Cost", "Token Reduction", "Latency Reduction", "Cost Reduction"].map((h) => (
                <th key={h} className="px-4 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {PIPELINES.map((pipeline) => {
              const m = summary[pipeline.id] || {};
              return (
                <tr key={pipeline.id} className="border-b border-[var(--border)] last:border-0">
                  <td className="px-4 py-4 font-semibold">{pipeline.label}</td>
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-1">
                      {winners.accuracy === pipeline.id && <Badge icon={Award}>Accuracy Winner</Badge>}
                      {winners.tokens === pipeline.id && <Badge icon={Medal}>Lowest Tokens</Badge>}
                      {winners.latency === pipeline.id && <Badge icon={Timer}>Fastest</Badge>}
                      {winners.overall === pipeline.id && <Badge icon={Gauge}>Best Overall</Badge>}
                    </div>
                  </td>
                  <td className="px-4 py-4">{formatRate(m.llm_judge_pass_rate)}</td>
                  <td className="px-4 py-4">{formatNumber(m.bertscore_f1, 3)}</td>
                  <td className="px-4 py-4">{formatNumber(m.avg_total_tokens, 0)}</td>
                  <td className="px-4 py-4">{formatNumber(m.avg_latency_seconds, 2)}s</td>
                  <td className="px-4 py-4">${formatNumber(m.avg_estimated_cost, 4)}</td>
                  <td className="px-4 py-4">{formatPercent(m.token_reduction_vs_llm_only)}</td>
                  <td className="px-4 py-4">{formatPercent(m.latency_reduction_vs_llm_only)}</td>
                  <td className="px-4 py-4">{formatPercent(m.cost_reduction_vs_llm_only)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <ResultsCharts summary={summary} />
    </SectionShell>
  );
}

function Badge({ children, icon: Icon }: { children: React.ReactNode; icon: typeof Award }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-md border border-blue-200 bg-blue-50 px-2 py-1 text-xs font-semibold text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-200">
      <Icon className="h-3 w-3" />
      {children}
    </span>
  );
}

function best(summary: FinalSummary, key: keyof NonNullable<FinalSummary["graphrag"]>, mode: "min" | "max") {
  const rows = PIPELINES.map((pipeline) => ({ id: pipeline.id, value: summary[pipeline.id]?.[key] }))
    .filter((row): row is { id: typeof PIPELINES[number]["id"]; value: number } => typeof row.value === "number");
  rows.sort((a, b) => (mode === "min" ? a.value - b.value : b.value - a.value));
  return rows[0]?.id || null;
}

function bestOverall(summary: FinalSummary) {
  const scores = PIPELINES.map((pipeline) => {
    const m = summary[pipeline.id] || {};
    const score =
      (m.llm_judge_pass_rate || 0) * 35 +
      (m.bertscore_f1 || 0) * 25 +
      Math.max(0, m.token_reduction_vs_llm_only || 0) * 0.15 +
      Math.max(0, m.latency_reduction_vs_llm_only || 0) * 0.1 +
      Math.max(0, m.cost_reduction_vs_llm_only || 0) * 0.15;
    return { id: pipeline.id, score };
  });
  scores.sort((a, b) => b.score - a.score);
  return scores[0]?.id || null;
}
