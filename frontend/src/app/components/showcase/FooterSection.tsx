import { DATASET_STATS, GITHUB_URL, SPACE_URL, VERCEL_URL } from "../../lib/showcase";

export function FooterSection() {
  const links = [
    ["GitHub Repository", GITHUB_URL],
    ["Dataset Source", DATASET_STATS.source],
    ["Hugging Face Space API", SPACE_URL],
    ["Vercel Deployment", VERCEL_URL],
  ];
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface)]">
      <div className="mx-auto flex w-full max-w-[1240px] flex-col gap-6 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="text-sm font-semibold text-[var(--text-primary)]">GraphRAG Benchmark</div>
          <div className="mt-1 text-sm text-[var(--text-secondary)]">Benchmarking Graph-Based Retrieval at Scale</div>
          <div className="mt-2 text-xs text-[var(--text-secondary)]">Author: Vedant Dhavan</div>
        </div>
        <div className="flex flex-wrap gap-3">
          {links.map(([label, href]) => (
            <a key={label} href={href} target="_blank" rel="noreferrer" className="text-sm font-semibold text-blue-600 dark:text-blue-300">
              {label}
            </a>
          ))}
        </div>
      </div>
    </footer>
  );
}
