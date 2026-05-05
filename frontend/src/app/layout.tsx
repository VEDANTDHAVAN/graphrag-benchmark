import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import Script from "next/script";
import "./globals.css";
import ThemeToggle from "./components/ThemeToggle";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GraphRAG Benchmark",
  description: "Benchmark LLM-only vs Basic RAG vs GraphRAG (local) side-by-side.",
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
      <head>
        <Script id="theme-init" strategy="beforeInteractive">
          {`
            (function () {
              try {
                var stored = localStorage.getItem("theme");
                var theme = stored === "light" || stored === "dark"
                  ? stored
                  : (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
                document.documentElement.classList.toggle("dark", theme === "dark");
              } catch (e) {}
            })();
          `}
        </Script>
      </head>
      <body className="min-h-full flex flex-col bg-[var(--background)] text-[var(--text-primary)]">
        <header className="border-b border-[var(--border)] bg-[var(--background)]/70 backdrop-blur">
          <div className="mx-auto flex w-full max-w-[1200px] items-center justify-between px-6 py-4">
            <Link href="/" className="text-sm font-semibold text-[var(--text-primary)]">
              GraphRAG Benchmark
            </Link>
            <nav className="flex items-center gap-2 text-sm">
              <Link
                href="/upload"
                className="inline-flex h-9 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 text-[var(--text-primary)] shadow-sm transition-colors hover:bg-white/60 dark:hover:bg-white/5"
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
                className="inline-flex h-9 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 text-[var(--text-primary)] shadow-sm transition-colors hover:bg-white/60 dark:hover:bg-white/5"
              >
                Graph
              </Link>
              <ThemeToggle />
            </nav>
          </div>
        </header>
        <div className="flex-1">{children}</div>
      </body>
    </html>
  );
}
