import {
  Blocks,
  Brain,
  CheckCircle2,
  Cloud,
  Cpu,
  Database,
  Gauge,
  GitBranch,
  Layers3,
  Network,
  Search,
  Server,
  ShieldCheck,
  TriangleAlert,
  type LucideIcon,
} from "lucide-react";
import { DATASET_STATS, SPACE_URL, VERCEL_URL } from "../../lib/showcase";
import { SectionShell } from "./SectionShell";

export function WhyGraphRAGSection() {
  const cards = [
    {
      title: "LLM-only",
      icon: Brain,
      body: "Fast to wire up, but answers are ungrounded and can hallucinate when the model lacks source context.",
    },
    {
      title: "Basic RAG",
      icon: Search,
      body: "Retrieves semantically similar chunks, but often misses relationships spread across documents or entities.",
    },
    {
      title: "GraphRAG",
      icon: Network,
      body: "Traverses entity and chunk relationships, enabling compact context and multi-hop reasoning over the corpus.",
    },
  ];
  return (
    <SectionShell id="why" eyebrow="Problem" title="Why GraphRAG matters" description="The benchmark asks whether graph-structured retrieval can keep answers grounded while reducing context bloat.">
      <div className="grid gap-4 md:grid-cols-3">
        {cards.map(({ title, icon: Icon, body }) => (
          <div key={title} className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm">
            <Icon className="h-6 w-6 text-blue-600 dark:text-blue-300" />
            <h3 className="mt-4 text-base font-semibold">{title}</h3>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{body}</p>
          </div>
        ))}
      </div>
    </SectionShell>
  );
}

export function DatasetSection() {
  const stats = [
    ["Dataset", `${DATASET_STATS.datasetName} (${DATASET_STATS.config})`],
    ["Domain", DATASET_STATS.domain],
    ["Total tokens", DATASET_STATS.totalTokens],
    ["Papers selected", DATASET_STATS.papers],
    ["Evaluation questions", DATASET_STATS.evalQuestions],
    ["Source", "Hugging Face arXiv split"],
  ];
  return (
    <SectionShell id="dataset" eyebrow="Corpus" title="A scientific-paper dataset with relationship density" description="Scientific papers naturally contain methods, datasets, tasks, assumptions, citations, and concepts that reward graph retrieval.">
      <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
          <Database className="h-6 w-6 text-blue-600 dark:text-blue-300" />
          <p className="mt-4 text-sm leading-6 text-[var(--text-secondary)]">
            The corpus is large enough to stress token budgets and rich enough to expose the difference between nearest-neighbor retrieval and graph-aware traversal.
          </p>
          <a className="mt-5 inline-flex text-sm font-semibold text-blue-600 dark:text-blue-300" href={DATASET_STATS.source} target="_blank" rel="noreferrer">
            View dataset source
          </a>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {stats.map(([label, value]) => (
            <div key={label} className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">{label}</div>
              <div className="mt-2 text-base font-semibold text-[var(--text-primary)]">{value}</div>
            </div>
          ))}
        </div>
      </div>
    </SectionShell>
  );
}

export function MethodologySection() {
  const rows = [
    ["LLM-only", "Direct prompt", "General parametric reasoning", "Simple baseline", "No retrieval grounding"],
    ["Basic RAG", "ChromaDB similarity search", "Single-hop semantic retrieval", "Strong factual grounding", "Can miss entity relationships"],
    ["GraphRAG", "NetworkX graph traversal", "Multi-hop entity context", "Compact relationship-aware evidence", "Depends on graph quality"],
  ];
  return (
    <SectionShell id="methodology" eyebrow="Benchmark Method" title="Same questions, three retrieval strategies" description="Every evaluation question is run through all three pipelines and scored with identical metrics.">
      <div className="overflow-x-auto rounded-xl border border-[var(--border)] bg-[var(--surface)]">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="border-b border-[var(--border)] text-xs uppercase tracking-wide text-[var(--text-secondary)]">
            <tr>
              {["Pipeline", "Retrieval strategy", "Reasoning", "Strength", "Limitation"].map((h) => (
                <th key={h} className="px-4 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row[0]} className="border-b border-[var(--border)] last:border-0">
                {row.map((cell, i) => (
                  <td key={cell} className={`px-4 py-4 ${i === 0 ? "font-semibold text-[var(--text-primary)]" : "text-[var(--text-secondary)]"}`}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionShell>
  );
}

export function AccuracySection() {
  const methods: Array<{ title: string; icon: LucideIcon; body: string }> = [
    {
      title: "LLM-as-a-Judge",
      icon: ShieldCheck,
      body: "A hosted Hugging Face model independently grades each answer PASS or FAIL against the reference answer.",
    },
    {
      title: "BERTScore",
      icon: Gauge,
      body: "Semantic similarity catches correct paraphrases using rescaled F1, reducing dependence on exact wording.",
    },
  ];
  return (
    <SectionShell id="accuracy" eyebrow="Evaluation" title="Two independent quality checks" description="Token reduction only matters when answers remain correct, grounded, and semantically aligned with references.">
      <div className="grid gap-4 md:grid-cols-2">
        {methods.map(({ title, icon: Icon, body }) => (
          <div key={title} className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
            <Icon className="h-6 w-6 text-blue-600 dark:text-blue-300" />
            <h3 className="mt-4 text-base font-semibold">{title}</h3>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{body}</p>
          </div>
        ))}
      </div>
      <div className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 text-sm leading-6 text-[var(--text-secondary)]">
        Judge model: <span className="font-semibold text-[var(--text-primary)]">meta-llama/Llama-3.1-8B-Instruct</span>. Evaluation set: <span className="font-semibold text-[var(--text-primary)]">40 grounded questions</span>.
      </div>
    </SectionShell>
  );
}

export function ArchitectureSection() {
  const layers: Array<{ title: string; body: string; icon: LucideIcon }> = [
    { title: "Frontend", body: "Vercel, Next.js, TypeScript, Tailwind CSS, shadcn-style UI, Framer Motion", icon: Cloud },
    { title: "Backend", body: "Hugging Face Spaces, FastAPI, Python", icon: Server },
    { title: "Retrieval", body: "ChromaDB vectors plus NetworkX graph traversal", icon: GitBranch },
    { title: "Evaluation", body: "Hugging Face Inference API and BERTScore", icon: CheckCircle2 },
    { title: "Optional connector", body: "TigerGraph for enterprise-scale graph storage", icon: Blocks },
  ];
  return (
    <SectionShell id="architecture" eyebrow="System Design" title="A lightweight architecture judges can reproduce" description="The production deployment works fully without TigerGraph. NetworkX is the canonical GraphRAG engine.">
      <div className="grid gap-3">
        {layers.map(({ title, body, icon: Icon }, index) => (
          <div key={title} className="grid gap-3 md:grid-cols-[180px_1fr]">
            <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
              <Icon className="h-5 w-5 text-blue-600 dark:text-blue-300" />
              <div className="mt-2 text-sm font-semibold">{title}</div>
            </div>
            <div className="flex items-center rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 text-sm text-[var(--text-secondary)]">
              {body}
            </div>
            {index < layers.length - 1 && <div className="hidden md:block" />}
          </div>
        ))}
      </div>
    </SectionShell>
  );
}

export function TechStackSection() {
  const groups = {
    Frontend: ["Next.js", "TypeScript", "Tailwind CSS", "shadcn/ui", "Framer Motion", "Recharts"],
    Backend: ["Python", "FastAPI", "datasets", "tiktoken", "sentence-transformers"],
    Retrieval: ["ChromaDB", "NetworkX"],
    Evaluation: ["huggingface_hub", "evaluate", "bert-score"],
    Deployment: ["Vercel", "Hugging Face Spaces", "Docker"],
  };
  return (
    <SectionShell id="stack" eyebrow="Tech Stack" title="Built from portable, judge-friendly pieces">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(groups).map(([group, items]) => (
          <div key={group} className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
            <Cpu className="h-5 w-5 text-blue-600 dark:text-blue-300" />
            <h3 className="mt-3 text-sm font-semibold">{group}</h3>
            <div className="mt-4 flex flex-wrap gap-2">
              {items.map((item) => (
                <span key={item} className="rounded-md border border-[var(--border)] bg-[var(--background)] px-2.5 py-1 text-xs font-semibold text-[var(--text-primary)]">{item}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </SectionShell>
  );
}

export function TigerGraphPivotSection() {
  const rows = [
    ["Multi-hop traversal", "Yes", "Yes"],
    ["Benchmark ready", "Yes", "Yes"],
    ["Zero setup", "Yes", "No"],
    ["Laptop friendly", "Yes", "No"],
    ["Enterprise scale", "Limited", "Excellent"],
    ["Required for benchmark", "Yes", "No"],
  ];
  return (
    <SectionShell id="pivot" eyebrow="Architecture Decision" title="Architectural Pivot: From TigerGraph to NetworkX" description="TigerGraph was explored as the graph database backend, but operational complexity distracted from the research question.">
      <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
          <TriangleAlert className="h-6 w-6 text-amber-500" />
          <p className="mt-4 text-sm leading-6 text-[var(--text-secondary)]">
            Authentication issues, Docker complexity, resource overhead, and infrastructure work made TigerGraph a poor default for hackathon judging. NetworkX preserves graph traversal and multi-hop reasoning while running entirely in Python.
          </p>
          <p className="mt-4 text-sm font-semibold text-[var(--text-primary)]">
            The benchmark demonstrates graph-based retrieval methodology, not dependence on a particular graph database.
          </p>
        </div>
        <div className="overflow-x-auto rounded-xl border border-[var(--border)] bg-[var(--surface)]">
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead className="border-b border-[var(--border)] text-xs uppercase tracking-wide text-[var(--text-secondary)]">
              <tr><th className="px-4 py-3">Capability</th><th className="px-4 py-3">NetworkX</th><th className="px-4 py-3">TigerGraph</th></tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row[0]} className="border-b border-[var(--border)] last:border-0">
                  {row.map((cell, i) => <td key={cell} className={`px-4 py-3 ${i === 0 ? "font-semibold" : "text-[var(--text-secondary)]"}`}>{cell}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </SectionShell>
  );
}

export function DeploymentSection() {
  return (
    <SectionShell id="deployment" eyebrow="Deployment" title="Free, reproducible, and TigerGraph-free by default">
      <div className="grid gap-4 md:grid-cols-3">
        {[
          ["Frontend", "Vercel hosts the Next.js dashboard.", VERCEL_URL],
          ["Backend", "Hugging Face Spaces runs the Dockerized FastAPI API.", SPACE_URL],
          ["Storage", "ChromaDB files, JSON artifacts, and NetworkX graph files are bundled with the backend.", ""],
        ].map(([title, body, href]) => (
          <div key={title} className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
            <Layers3 className="h-5 w-5 text-blue-600 dark:text-blue-300" />
            <h3 className="mt-3 text-sm font-semibold">{title}</h3>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{body}</p>
            {href && <a href={href} target="_blank" rel="noreferrer" className="mt-4 inline-flex text-sm font-semibold text-blue-600 dark:text-blue-300">Open deployment</a>}
          </div>
        ))}
      </div>
    </SectionShell>
  );
}
