export type PipelineId = "llm_only" | "basic_rag" | "graphrag";

export type SummaryMetrics = {
  avg_total_tokens?: number | null;
  avg_latency_seconds?: number | null;
  avg_estimated_cost?: number | null;
  llm_judge_pass_rate?: number | null;
  bertscore_f1?: number | null;
  token_reduction_vs_llm_only?: number | null;
  latency_reduction_vs_llm_only?: number | null;
  cost_reduction_vs_llm_only?: number | null;
};

export type FinalSummary = Partial<Record<PipelineId, SummaryMetrics>>;

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
export const GITHUB_URL =
  process.env.NEXT_PUBLIC_GITHUB_URL || "https://github.com/VedantDhavan/graphrag-benchmark";
export const SPACE_URL =
  process.env.NEXT_PUBLIC_HF_SPACE_URL || "https://vedantdhavan-graphrag-benchmark.hf.space";
export const VERCEL_URL =
  process.env.NEXT_PUBLIC_VERCEL_URL || "https://graphrag-benchmark.vercel.app";

export const PIPELINES: Array<{ id: PipelineId; label: string; short: string }> = [
  { id: "llm_only", label: "LLM-only", short: "LLM" },
  { id: "basic_rag", label: "Basic RAG", short: "RAG" },
  { id: "graphrag", label: "GraphRAG", short: "Graph" },
];

export const FALLBACK_SUMMARY: FinalSummary = {
  llm_only: {
    avg_total_tokens: 391,
    avg_latency_seconds: 5.53,
    avg_estimated_cost: 0.0008,
    llm_judge_pass_rate: 0.82,
    bertscore_f1: 0.57,
    token_reduction_vs_llm_only: 0,
    latency_reduction_vs_llm_only: 0,
    cost_reduction_vs_llm_only: 0,
  },
  basic_rag: {
    avg_total_tokens: 650,
    avg_latency_seconds: 1.69,
    avg_estimated_cost: 0.0013,
    llm_judge_pass_rate: 0.88,
    bertscore_f1: 0.61,
    token_reduction_vs_llm_only: -66.2,
    latency_reduction_vs_llm_only: 69.4,
    cost_reduction_vs_llm_only: -66.2,
  },
  graphrag: {
    avg_total_tokens: 377,
    avg_latency_seconds: 1.45,
    avg_estimated_cost: 0.00075,
    llm_judge_pass_rate: 0.9,
    bertscore_f1: 0.64,
    token_reduction_vs_llm_only: 3.6,
    latency_reduction_vs_llm_only: 73.8,
    cost_reduction_vs_llm_only: 3.6,
  },
};

export const DATASET_STATS = {
  datasetName: "armanc/scientific_papers",
  config: "arxiv",
  domain: "Scientific Research Papers",
  totalTokens: "2,004,563",
  papers: "220",
  evalQuestions: "40",
  source: "https://huggingface.co/datasets/armanc/scientific_papers",
};

export function formatNumber(value?: number | null, digits = 0) {
  if (typeof value !== "number") return "N/A";
  return value.toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

export function formatPercent(value?: number | null, digits = 1) {
  if (typeof value !== "number") return "N/A";
  return `${value.toFixed(digits)}%`;
}

export function formatRate(value?: number | null) {
  if (typeof value !== "number") return "N/A";
  return formatPercent(value * 100, 1);
}

export async function getFinalSummary(): Promise<{ summary: FinalSummary; source: "api" | "fallback" }> {
  try {
    const response = await fetch(`${API_URL}/api/metrics/final-summary`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });
    if (!response.ok) throw new Error("summary unavailable");
    const data = await response.json();
    if (data?.status === "ok" && data?.summary) {
      return { summary: data.summary, source: "api" };
    }
  } catch {
    // Fallback keeps the landing page useful during cold starts and local setup.
  }
  return { summary: FALLBACK_SUMMARY, source: "fallback" };
}
