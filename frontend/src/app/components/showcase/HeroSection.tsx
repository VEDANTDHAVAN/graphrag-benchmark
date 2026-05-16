import Link from "next/link";
import { ArrowRight, Database, GitBranch, LucideIcon, Scale, ShieldCheck, Sparkles } from "lucide-react";
import { GITHUB_URL } from "../../lib/showcase";

const badges = [
  "2M Tokens",
  "3 Pipelines",
  "40 Evaluation Questions",
  "LLM Judge + BERTScore",
  "Vercel + Hugging Face Spaces",
];

const heroMetrics: Array<{ label: string; value: string; icon: LucideIcon }> = [
  { label: "Corpus scale", value: "2,004,563 tokens", icon: Database },
  { label: "Retrieval strategy", value: "Vector similarity + graph traversal", icon: GitBranch },
  { label: "Evaluation", value: "Independent judge and semantic validator", icon: ShieldCheck },
  { label: "Outcome", value: "Efficiency without cutting accuracy", icon: Scale },
];

export function HeroSection() {
  return (
    <section id="hero" className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10 opacity-80 dark:opacity-50">
        <GraphBackdrop />
      </div>
      <div className="mx-auto grid min-h-[calc(100vh-58px)] w-full max-w-[1240px] items-center gap-10 px-4 py-14 sm:px-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-200">
            <Sparkles className="h-3.5 w-3.5" />
            Research benchmark portal
          </div>
          <h1 className="mt-5 max-w-4xl text-4xl font-semibold tracking-tight text-[var(--text-primary)] sm:text-6xl">
            GraphRAG Benchmark: Proving Graph-Based Retrieval at Scale
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-[var(--text-secondary)] sm:text-lg">
            A 2 million token benchmark comparing LLM-only, Basic RAG, and NetworkX GraphRAG using long-form scientific papers.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {badges.map((badge) => (
              <span key={badge} className="rounded-md border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-xs font-semibold text-[var(--text-primary)]">
                {badge}
              </span>
            ))}
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/benchmark" className="inline-flex h-11 items-center gap-2 rounded-lg bg-blue-600 px-5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700">
              Run Benchmark <ArrowRight className="h-4 w-4" />
            </Link>
            <a href="#architecture" className="inline-flex h-11 items-center rounded-lg border border-[var(--border)] bg-[var(--surface)] px-5 text-sm font-semibold text-[var(--text-primary)] shadow-sm transition-colors hover:bg-white/70 dark:hover:bg-white/5">
              Explore Architecture
            </a>
            <a href={GITHUB_URL} target="_blank" rel="noreferrer" className="inline-flex h-11 items-center rounded-lg border border-[var(--border)] px-5 text-sm font-semibold text-[var(--text-primary)] transition-colors hover:bg-[var(--surface)]">
              View GitHub
            </a>
          </div>
        </div>
        <div className="grid gap-3">
          {heroMetrics.map(({ label, value, icon: Icon }) => (
            <div key={label} className="rounded-xl border border-[var(--border)] bg-[var(--surface)]/85 p-5 shadow-sm backdrop-blur">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-blue-100 p-2 text-blue-700 dark:bg-blue-950 dark:text-blue-200">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">{label}</div>
                  <div className="mt-1 text-lg font-semibold text-[var(--text-primary)]">{value}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function GraphBackdrop() {
  return (
    <svg className="h-full w-full" viewBox="0 0 1200 720" role="presentation" aria-hidden="true">
      <defs>
        <linearGradient id="line" x1="0" x2="1">
          <stop stopColor="#2563eb" stopOpacity="0.2" />
          <stop offset="1" stopColor="#14b8a6" stopOpacity="0.28" />
        </linearGradient>
      </defs>
      {[
        [120, 160, 360, 110],
        [360, 110, 610, 230],
        [610, 230, 910, 140],
        [260, 430, 610, 230],
        [610, 230, 810, 500],
        [130, 580, 260, 430],
        [810, 500, 1080, 420],
      ].map(([x1, y1, x2, y2], i) => (
        <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="url(#line)" strokeWidth="2" />
      ))}
      {[120, 360, 610, 910, 260, 810, 1080, 130].map((x, i) => {
        const y = [160, 110, 230, 140, 430, 500, 420, 580][i];
        return <circle key={i} cx={x} cy={y} r="7" fill="#2563eb" opacity="0.35" />;
      })}
    </svg>
  );
}
