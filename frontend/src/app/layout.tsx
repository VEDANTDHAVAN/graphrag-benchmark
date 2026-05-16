import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import ThemeToggle from "./components/ThemeToggle";
import { ThemeProvider } from "./components/providers/ThemeProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://graphrag-benchmark.vercel.app"),
  title: "GraphRAG Benchmark | 2M Token Evaluation of LLM-only vs RAG vs GraphRAG",
  description:
    "A 2 million token scientific-paper benchmark comparing LLM-only, Basic RAG, and NetworkX GraphRAG with LLM judge and BERTScore evaluation.",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "GraphRAG Benchmark",
    description:
      "A reproducible benchmark proving graph-based retrieval at scientific-paper scale.",
    url: "https://graphrag-benchmark.vercel.app",
    siteName: "GraphRAG Benchmark",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "GraphRAG Benchmark",
    description:
      "2M-token evaluation of LLM-only vs Basic RAG vs GraphRAG using scientific papers.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[var(--background)] text-[var(--text-primary)]">
        <ThemeProvider>
          <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--background)]/80 backdrop-blur-xl">
            <div className="mx-auto flex w-full max-w-[1240px] items-center justify-between px-4 py-3 sm:px-6">
              <Link href="/" className="text-sm font-semibold text-[var(--text-primary)]">
                GraphRAG Benchmark
              </Link>
              <nav className="flex items-center gap-2 text-sm">
                <Link
                  href="/upload"
                  className="hidden h-9 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 text-[var(--text-primary)] shadow-sm transition-colors hover:bg-white/60 sm:inline-flex dark:hover:bg-white/5"
                >
                  Upload
                </Link>
                <Link
                  href="/benchmark"
                  className="inline-flex h-9 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 text-[var(--text-primary)] shadow-sm transition-colors hover:bg-white/60 dark:hover:bg-white/5"
                >
                  Benchmark
                </Link>
                <Link
                  href="/graph"
                  className="hidden h-9 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 text-[var(--text-primary)] shadow-sm transition-colors hover:bg-white/60 sm:inline-flex dark:hover:bg-white/5"
                >
                  Graph
                </Link>
                <ThemeToggle />
              </nav>
            </div>
          </header>
          <div className="flex-1">{children}</div>
        </ThemeProvider>
      </body>
    </html>
  );
}
