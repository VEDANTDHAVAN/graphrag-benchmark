"use client";

import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { Button } from "../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/Card";

type PipelineId = "llm_only" | "basic_rag" | "graphrag";

type PipelineResult = {
  status: "success" | "error";
  answer?: string;
  context?: string;
  tokens?: number;
  latency?: number;
  accuracy?: {
    llm_judge?: string;
    llm_judge_pass?: boolean;
    bertscore_f1?: number | null;
  };
  error?: string;
  details?: any;
};

type QueryResponse = {
  query: string;
  pipelines: Record<PipelineId, PipelineResult>;
};

type SummaryMetrics = {
  avg_total_tokens?: number | null;
  avg_latency_seconds?: number | null;
  avg_estimated_cost?: number | null;
  llm_judge_pass_rate?: number | null;
  bertscore_f1?: number | null;
  token_reduction_vs_llm_only?: number | null;
  latency_reduction_vs_llm_only?: number | null;
  cost_reduction_vs_llm_only?: number | null;
};

type FinalSummaryResponse = {
  status: string;
  summary: Partial<Record<PipelineId, SummaryMetrics>>;
};

const PIPELINES: Array<{ id: PipelineId; label: string; accent: string }> = [
  { id: "llm_only", label: "LLM Only", accent: "border-slate-400" },
  { id: "basic_rag", label: "Basic RAG", accent: "border-emerald-500" },
  { id: "graphrag", label: "GraphRAG", accent: "border-amber-500" },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function formatDelta(n: number) {
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}`;
}

function formatNumber(value?: number | null, digits = 2) {
  return typeof value === "number" ? value.toFixed(digits) : "N/A";
}

function formatPercent(value?: number | null, digits = 1) {
  return typeof value === "number" ? `${value.toFixed(digits)}%` : "N/A";
}

function formatRate(value?: number | null) {
  return typeof value === "number" ? formatPercent(value * 100) : "N/A";
}

export default function BenchmarkPage() {
  const [query, setQuery] = useState("What is the main contribution or focus of the paper about laser beams propagating through turbulent atmospheres?");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [summary, setSummary] = useState<FinalSummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/metrics/final-summary`)
      .then((response) => response.json())
      .then((data) => setSummary(data))
      .catch(() => setSummary({ status: "missing", summary: {} }));
  }, []);

  const comparison = useMemo(() => {
    const basic = result?.pipelines.basic_rag;
    const graph = result?.pipelines.graphrag;
    if (!basic || !graph) return null;
    if (basic.status !== "success" || graph.status !== "success") return null;
    const basicTokens = basic.tokens ?? 0;
    const graphTokens = graph.tokens ?? 0;
    const basicLatency = basic.latency ?? 0;
    const graphLatency = graph.latency ?? 0;
    return {
      tokenReductionAbs: basicTokens - graphTokens,
      tokenReductionPct: basicTokens > 0 ? ((basicTokens - graphTokens) / basicTokens) * 100 : 0,
      latencyReductionAbs: basicLatency - graphLatency,
      latencyReductionPct:
        basicLatency > 0 ? ((basicLatency - graphLatency) / basicLatency) * 100 : 0,
    };
  }, [result]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: trimmed, run_all: true }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(typeof data.detail === "string" ? data.detail : "Query failed");
      }
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setLoading(false);
    }
  };

  const graphragDetails = result?.pipelines.graphrag?.details;
  const summaryData = summary?.summary ?? {};
  const summaryValues = PIPELINES.map((pipeline) => ({
    ...pipeline,
    metrics: summaryData[pipeline.id],
  }));
  const accuracyWinner = bestPipeline(summaryData, "llm_judge_pass_rate", "max");
  const lowestToken = bestPipeline(summaryData, "avg_total_tokens", "min");
  const fastest = bestPipeline(summaryData, "avg_latency_seconds", "min");
  const bestOverall = bestOverallPipeline(summaryData);

  return (
    <main className="mx-auto flex w-full max-w-[1200px] flex-col gap-6 px-6 py-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Benchmark</h1>
        <p className="text-sm text-[var(--text-secondary)]">
          Compare LLM-only, Basic RAG (ChromaDB), and GraphRAG (NetworkX).
        </p>
      </header>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>Final Benchmark Summary</CardTitle>
            <CardDescription>
              Accuracy, efficiency, and cost from the 2M-token scientific benchmark.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          {summary?.status !== "ok" ? (
            <p className="text-sm text-[var(--text-secondary)]">
              Run the full benchmark workflow to populate final_summary.json.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] text-left text-sm">
                <thead className="border-b border-[var(--border)] text-xs uppercase tracking-wide text-[var(--text-secondary)]">
                  <tr>
                    <th className="py-2 pr-3">Pipeline</th>
                    <th className="px-3 py-2">Badges</th>
                    <th className="px-3 py-2">LLM Judge</th>
                    <th className="px-3 py-2">BERTScore F1</th>
                    <th className="px-3 py-2">Avg Tokens</th>
                    <th className="px-3 py-2">Avg Latency</th>
                    <th className="px-3 py-2">Avg Cost</th>
                    <th className="px-3 py-2">Token Reduction</th>
                    <th className="px-3 py-2">Latency Reduction</th>
                    <th className="px-3 py-2">Cost Reduction</th>
                  </tr>
                </thead>
                <tbody>
                  {summaryValues.map((item) => (
                    <tr key={item.id} className="border-b border-[var(--border)] last:border-0">
                      <td className="py-3 pr-3 font-semibold text-[var(--text-primary)]">
                        {item.label}
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex flex-wrap gap-1">
                          {accuracyWinner === item.id && <Badge>Accuracy Winner</Badge>}
                          {lowestToken === item.id && <Badge>Lowest Token Usage</Badge>}
                          {fastest === item.id && <Badge>Fastest Pipeline</Badge>}
                          {bestOverall === item.id && <Badge>Best Overall</Badge>}
                        </div>
                      </td>
                      <td className="px-3 py-3">{formatRate(item.metrics?.llm_judge_pass_rate)}</td>
                      <td className="px-3 py-3">{formatNumber(item.metrics?.bertscore_f1, 3)}</td>
                      <td className="px-3 py-3">{formatNumber(item.metrics?.avg_total_tokens, 0)}</td>
                      <td className="px-3 py-3">{formatNumber(item.metrics?.avg_latency_seconds)}s</td>
                      <td className="px-3 py-3">${formatNumber(item.metrics?.avg_estimated_cost, 4)}</td>
                      <td className="px-3 py-3">{formatPercent(item.metrics?.token_reduction_vs_llm_only)}</td>
                      <td className="px-3 py-3">{formatPercent(item.metrics?.latency_reduction_vs_llm_only)}</td>
                      <td className="px-3 py-3">{formatPercent(item.metrics?.cost_reduction_vs_llm_only)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>Query</CardTitle>
            <CardDescription>Run all pipelines against the same prompt.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              rows={3}
              className="min-h-24 w-full resize-y rounded-lg border border-[var(--border)] bg-[var(--background)] p-3 text-sm leading-6 text-[var(--text-primary)] outline-none"
              placeholder="Ask something about the uploaded papers…"
            />
            <div className="flex items-center justify-between gap-3">
              <div className="text-xs text-[var(--text-secondary)]">
                Tip: use terms from the title/abstract for more stable comparisons.
              </div>
              <Button type="submit" disabled={loading || !query.trim()} variant="primary" className="h-10">
                {loading ? "Running" : "Run All Pipelines"}
              </Button>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
          </form>
        </CardContent>
      </Card>

      {comparison && (
        <Card>
          <CardHeader>
            <div>
              <CardTitle>GraphRAG vs Basic RAG</CardTitle>
              <CardDescription>
                Positive values indicate GraphRAG uses fewer resources than Basic RAG.
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3">
              <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                Token Reduction
              </div>
              <div className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
                {comparison.tokenReductionAbs} ({formatDelta(comparison.tokenReductionPct)}%)
              </div>
            </div>
            <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3">
              <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                Latency Reduction
              </div>
              <div className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
                {comparison.latencyReductionAbs.toFixed(2)}s ({formatDelta(comparison.latencyReductionPct)}%)
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <section className="grid gap-4 xl:grid-cols-3">
        {PIPELINES.map((pipeline) => {
          const item = result?.pipelines[pipeline.id];
          return (
            <Card key={pipeline.id} className={`border-t-4 ${pipeline.accent}`}>
              <CardHeader className="py-3">
                <div className="flex-1">
                  <div className="text-sm font-semibold text-[var(--text-primary)]">{pipeline.label}</div>
                  {item && (
                    <div className="mt-1 text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                      {item.status}
                    </div>
                  )}
                </div>
                {item?.status === "success" && (
                  <div className="text-right text-xs text-[var(--text-secondary)]">
                    <div>{item.latency?.toFixed(2)}s</div>
                    <div>{item.tokens ?? 0} tokens</div>
                  </div>
                )}
              </CardHeader>

              {!item && (
                <div className="flex min-h-72 items-center justify-center px-5 py-4 text-sm text-[var(--text-secondary)]">
                  {loading ? "Waiting" : "No result"}
                </div>
              )}

              {item?.status === "error" && (
                <CardContent>
                  <p className="whitespace-pre-wrap text-sm text-red-700">{item.error}</p>
                </CardContent>
              )}

              {item?.status === "success" && (
                <CardContent className="flex flex-col gap-4">
                  <section>
                    <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                      Answer
                    </h3>
                    <p className="whitespace-pre-wrap text-sm leading-6 text-[var(--text-primary)]">
                      {item.answer}
                    </p>
                  </section>

                  {item.accuracy && (
                    <section className="grid gap-2 sm:grid-cols-2">
                      <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3">
                        <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                          LLM Judge
                        </div>
                        <div className="mt-1 text-sm font-semibold text-[var(--text-primary)]">
                          {item.accuracy.llm_judge ?? "SKIP"}
                        </div>
                      </div>
                      <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3">
                        <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                          BERTScore F1
                        </div>
                        <div className="mt-1 text-sm font-semibold text-[var(--text-primary)]">
                          {typeof item.accuracy.bertscore_f1 === "number"
                            ? item.accuracy.bertscore_f1.toFixed(3)
                            : "SKIP"}
                        </div>
                      </div>
                    </section>
                  )}

                  <details className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2" open={pipeline.id !== "llm_only"}>
                    <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                      Context Used
                    </summary>
                    <pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 text-xs leading-5 text-[var(--text-primary)]">
                      {item.context || "(none)"}
                    </pre>
                  </details>
                </CardContent>
              )}
            </Card>
          );
        })}
      </section>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>GraphRAG Details</CardTitle>
            <CardDescription>Matched entities, reasoning paths, and selected chunks.</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          {!graphragDetails ? (
            <p className="text-sm text-[var(--text-secondary)]">Run a query to see graph details.</p>
          ) : (
            <div className="grid gap-3 lg:grid-cols-3">
              <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3">
                <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                  Matched Entities
                </div>
                <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap text-xs text-[var(--text-primary)]">
                  {JSON.stringify(graphragDetails.matched_entities ?? [], null, 2)}
                </pre>
              </div>
              <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3">
                <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                  Reasoning Paths
                </div>
                <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap text-xs text-[var(--text-primary)]">
                  {JSON.stringify(graphragDetails.reasoning_paths ?? [], null, 2)}
                </pre>
              </div>
              <div className="rounded-lg border border-[var(--border)] bg-[var(--background)] p-3">
                <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                  Graph Chunks Used
                </div>
                <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap text-xs text-[var(--text-primary)]">
                  {JSON.stringify(
                    (graphragDetails.chunks ?? []).map((c: any) => ({
                      chunk_id: c.chunk_id,
                      doc_id: c.doc_id,
                    })),
                    null,
                    2
                  )}
                </pre>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </main>
  );
}

function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-md border border-blue-200 bg-blue-50 px-2 py-1 text-xs font-semibold text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-200">
      {children}
    </span>
  );
}

function bestPipeline(
  summary: Partial<Record<PipelineId, SummaryMetrics>>,
  key: keyof SummaryMetrics,
  mode: "min" | "max"
) {
  const candidates = PIPELINES.map((pipeline) => ({
    id: pipeline.id,
    value: summary[pipeline.id]?.[key],
  })).filter((item): item is { id: PipelineId; value: number } => typeof item.value === "number");

  if (!candidates.length) return null;
  candidates.sort((a, b) => (mode === "min" ? a.value - b.value : b.value - a.value));
  return candidates[0].id;
}

function bestOverallPipeline(summary: Partial<Record<PipelineId, SummaryMetrics>>) {
  const scores = PIPELINES.map((pipeline) => {
    const metrics = summary[pipeline.id];
    if (!metrics) return { id: pipeline.id, score: -Infinity };
    const accuracy = (metrics.llm_judge_pass_rate ?? 0) * 100;
    const bert = (metrics.bertscore_f1 ?? 0) * 100;
    const tokens = metrics.token_reduction_vs_llm_only ?? 0;
    const latency = metrics.latency_reduction_vs_llm_only ?? 0;
    const cost = metrics.cost_reduction_vs_llm_only ?? 0;
    return {
      id: pipeline.id,
      score: accuracy * 0.35 + bert * 0.25 + tokens * 0.15 + latency * 0.1 + cost * 0.15,
    };
  });
  scores.sort((a, b) => b.score - a.score);
  return scores[0]?.score === -Infinity ? null : scores[0]?.id;
}
