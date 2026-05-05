"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

type PipelineResult = {
  status: "success" | "error";
  answer?: string;
  context?: string;
  tokens?: number;
  latency?: number;
  error?: string;
  details?: Record<string, unknown>;
};

type QueryResponse = {
  query: string;
  pipelines: Record<"llm_only" | "basic_rag" | "graphrag", PipelineResult>;
};

const PIPELINES: Array<{
  id: keyof QueryResponse["pipelines"];
  label: string;
  accent: string;
}> = [
  { id: "llm_only", label: "LLM Only", accent: "border-slate-400" },
  { id: "basic_rag", label: "Basic RAG", accent: "border-emerald-500" },
  { id: "graphrag", label: "GraphRAG", accent: "border-amber-500" },
];

export default function Home() {
  const [query, setQuery] = useState("What does RAG-HAT do for hallucination in RAG?");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
        body: JSON.stringify({ query: trimmed }),
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

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-950">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-5 py-6">
        <header className="flex flex-col gap-3 border-b border-neutral-200 pb-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">GraphRAG Benchmark</h1>
            <p className="mt-1 text-sm text-neutral-600">
              Compare LLM-only, vector RAG, and graph-guided retrieval.
            </p>
          </div>
          <Link
            href="/upload"
            className="inline-flex h-10 items-center justify-center border border-neutral-300 bg-white px-4 text-sm font-medium hover:bg-neutral-100"
          >
            Upload PDF
          </Link>
        </header>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3 border-b border-neutral-200 pb-6">
          <label htmlFor="query" className="text-sm font-medium text-neutral-700">
            Query
          </label>
          <div className="grid gap-3 lg:grid-cols-[1fr_auto]">
            <textarea
              id="query"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              rows={3}
              className="min-h-24 resize-y border border-neutral-300 bg-white p-3 text-base outline-none focus:border-neutral-900"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="h-12 border border-neutral-950 bg-neutral-950 px-6 text-sm font-semibold text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:border-neutral-300 disabled:bg-neutral-300"
            >
              {loading ? "Running" : "Run"}
            </button>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </form>

        <section className="grid gap-4 xl:grid-cols-3">
          {PIPELINES.map((pipeline) => {
            const item = result?.pipelines[pipeline.id];
            return (
              <article
                key={pipeline.id}
                className={`min-h-96 border-t-4 ${pipeline.accent} bg-white p-4 shadow-sm`}
              >
                <div className="flex items-start justify-between gap-3 border-b border-neutral-200 pb-3">
                  <div>
                    <h2 className="text-lg font-semibold">{pipeline.label}</h2>
                    {item && (
                      <p className="mt-1 text-xs uppercase tracking-wide text-neutral-500">
                        {item.status}
                      </p>
                    )}
                  </div>
                  {item?.status === "success" && (
                    <div className="text-right text-xs text-neutral-600">
                      <div>{item.latency?.toFixed(2)}s</div>
                      <div>{item.tokens ?? 0} tokens</div>
                    </div>
                  )}
                </div>

                {!item && (
                  <div className="flex min-h-72 items-center justify-center text-sm text-neutral-500">
                    {loading ? "Waiting" : "No result"}
                  </div>
                )}

                {item?.status === "error" && (
                  <p className="mt-4 whitespace-pre-wrap text-sm text-red-700">{item.error}</p>
                )}

                {item?.status === "success" && (
                  <div className="mt-4 flex flex-col gap-4">
                    <section>
                      <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
                        Answer
                      </h3>
                      <p className="whitespace-pre-wrap text-sm leading-6">{item.answer}</p>
                    </section>

                    {item.context && (
                      <details className="border-t border-neutral-200 pt-3">
                        <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-neutral-500">
                          Context
                        </summary>
                        <pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap bg-neutral-50 p-3 text-xs leading-5 text-neutral-700">
                          {item.context}
                        </pre>
                      </details>
                    )}

                    {item.details && (
                      <details className="border-t border-neutral-200 pt-3">
                        <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-neutral-500">
                          Details
                        </summary>
                        <pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap bg-neutral-50 p-3 text-xs leading-5 text-neutral-700">
                          {JSON.stringify(item.details, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                )}
              </article>
            );
          })}
        </section>
      </div>
    </main>
  );
}
