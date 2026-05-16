"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { FinalSummary, PIPELINES } from "../../lib/showcase";

export function ResultsCharts({ summary }: { summary: FinalSummary }) {
  const bars = PIPELINES.map((pipeline) => {
    const metrics = summary[pipeline.id] || {};
    return {
      name: pipeline.short,
      tokens: Math.round(metrics.avg_total_tokens || 0),
      latency: Number((metrics.avg_latency_seconds || 0).toFixed(2)),
      accuracy: Number(((metrics.llm_judge_pass_rate || 0) * 100).toFixed(1)),
      bert: Number(((metrics.bertscore_f1 || 0) * 100).toFixed(1)),
    };
  });

  const radar = [
    { metric: "Accuracy", graphrag: score(summary.graphrag?.llm_judge_pass_rate, 1), rag: score(summary.basic_rag?.llm_judge_pass_rate, 1), llm: score(summary.llm_only?.llm_judge_pass_rate, 1) },
    { metric: "BERT", graphrag: score(summary.graphrag?.bertscore_f1, 1), rag: score(summary.basic_rag?.bertscore_f1, 1), llm: score(summary.llm_only?.bertscore_f1, 1) },
    { metric: "Token", graphrag: inverse(summary.graphrag?.avg_total_tokens, bars), rag: inverse(summary.basic_rag?.avg_total_tokens, bars), llm: inverse(summary.llm_only?.avg_total_tokens, bars) },
    { metric: "Latency", graphrag: inverse(summary.graphrag?.avg_latency_seconds, bars, "latency"), rag: inverse(summary.basic_rag?.avg_latency_seconds, bars, "latency"), llm: inverse(summary.llm_only?.avg_latency_seconds, bars, "latency") },
  ];

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <ChartCard title="Accuracy and semantic similarity">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={bars}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.25)" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="accuracy" fill="#2563eb" name="Judge pass %" radius={[4, 4, 0, 0]} />
            <Bar dataKey="bert" fill="#14b8a6" name="BERTScore x100" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Normalized overall profile">
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={radar}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" />
            <Tooltip />
            <Radar name="GraphRAG" dataKey="graphrag" stroke="#2563eb" fill="#2563eb" fillOpacity={0.25} />
            <Radar name="Basic RAG" dataKey="rag" stroke="#14b8a6" fill="#14b8a6" fillOpacity={0.18} />
            <Radar name="LLM" dataKey="llm" stroke="#64748b" fill="#64748b" fillOpacity={0.12} />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Average token usage">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={bars}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.25)" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="tokens" fill="#1d4ed8" name="Avg tokens" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Average latency">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={bars}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.25)" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="latency" fill="#0f766e" name="Seconds" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <h3 className="mb-4 text-sm font-semibold text-[var(--text-primary)]">{title}</h3>
      {children}
    </div>
  );
}

function score(value?: number | null, max = 1) {
  if (typeof value !== "number" || max === 0) return 0;
  return Math.max(0, Math.min(100, (value / max) * 100));
}

function inverse(value: number | null | undefined, rows: Array<Record<string, number | string>>, key = "tokens") {
  if (typeof value !== "number" || value <= 0) return 0;
  const values = rows.map((row) => Number(row[key])).filter(Boolean);
  const max = Math.max(...values);
  const min = Math.min(...values);
  if (max === min) return 100;
  return Math.max(0, Math.min(100, ((max - value) / (max - min)) * 100));
}
