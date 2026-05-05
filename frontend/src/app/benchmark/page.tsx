"use client";

import { FormEvent, useMemo, useState } from "react";
import { Button } from "../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/Card";

type PipelineId = "llm_only" | "basic_rag" | "graphrag";

type PipelineResult = {
  status: "success" | "error";
  answer?: string;
  context?: string;
  tokens?: number;
  latency?: number;
  error?: string;
  details?: any;
};

type QueryResponse = {
  query: string;
  pipelines: Record<PipelineId, PipelineResult>;
};

const PIPELINES: Array<{ id: PipelineId; label: string; accent: string }> = [
  { id: "llm_only", label: "LLM Only", accent: "border-slate-400" },
  { id: "basic_rag", label: "Basic RAG", accent: "border-emerald-500" },
  { id: "graphrag", label: "GraphRAG", accent: "border-amber-500" },
];

function formatDelta(n: number) {
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}`;
}

export default function BenchmarkPage() {
  const [query, setQuery] = useState("What does RAG-HAT do for hallucination in RAG?");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/query`, {
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

