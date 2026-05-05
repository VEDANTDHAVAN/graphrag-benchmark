"use client";

import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/Card";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Home() {
  return (
    <main>
      <div className="mx-auto flex w-full max-w-[1200px] flex-col gap-8 px-6 py-8">
        <header className="flex flex-col gap-3">
          <h1 className="text-3xl font-semibold text-[var(--text-primary)]">
            GraphRAG Benchmark
          </h1>
          <p className="text-sm leading-6 text-[var(--text-secondary)]">
            A local benchmark harness to compare three pipelines side-by-side:
            <span className="font-medium"> LLM-only</span>,{" "}
            <span className="font-medium">Basic RAG (ChromaDB)</span>, and{" "}
            <span className="font-medium">GraphRAG (NetworkX)</span>.
          </p>
        </header>

        <section className="grid gap-3 sm:grid-cols-3">
          {[
            {
              href: "/upload",
              title: "1. Upload Files",
              desc: "Ingest papers into ChromaDB + the local knowledge graph.",
            },
            {
              href: "/benchmark",
              title: "2. Run Benchmark",
              desc: "Compare answers, tokens, latency, and context side-by-side.",
            },
            {
              href: "/graph",
              title: "3. Inspect Graph",
              desc: "Visualize nodes and edges from NetworkX ingestion.",
            },
          ].map((item) => (
            <Link key={item.href} href={item.href} className="block">
              <Card className="transition-colors hover:bg-white/60 dark:hover:bg-white/5">
                <CardContent className="px-5 py-4">
                  <div className="text-sm font-semibold text-[var(--text-primary)]">
                    {item.title}
                  </div>
                  <div className="mt-1 text-xs text-[var(--text-secondary)]">
                    {item.desc}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </section>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Operating Guidelines</CardTitle>
              <CardDescription>Keep the demo smooth and repeatable.</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-5 text-sm text-[var(--text-primary)]">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                  Startup Order
                </div>
                <ol className="mt-2 list-decimal space-y-1 pl-5">
                  <li>
                    Start the backend API (FastAPI) and confirm{" "}
                    <span className="font-mono">{API_URL}/health</span> returns{" "}
                    <span className="font-mono">{"{status: ok}"}</span>.
                  </li>
                  <li>Start the frontend and open the app in a browser.</li>
                  <li>Upload one or more PDFs before benchmarking queries.</li>
                </ol>
              </div>

              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                  Smooth Demos
                </div>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li>
                    Keep queries specific (use key terms from title/abstract) to get more
                    stable comparisons.
                  </li>
                  <li>
                    Uploading the same PDF multiple times increases noise; prefer one
                    clean ingestion run per doc.
                  </li>
                  <li>
                    If results look off, re-upload the paper and rerun the same query to
                    compare pipelines under identical inputs.
                  </li>
                </ul>
              </div>

              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                  What Each Pipeline Uses
                </div>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  <li>LLM-only: no retrieved context.</li>
                  <li>Basic RAG: top chunks from ChromaDB similarity search.</li>
                  <li>
                    GraphRAG: graph-traversed chunks via entities/relations in NetworkX (plus a
                    compact context builder).
                  </li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <footer className="text-xs text-[var(--text-secondary)]">
          API: <span className="font-mono">{API_URL}</span>
        </footer>
      </div>
    </main>
  );
}
