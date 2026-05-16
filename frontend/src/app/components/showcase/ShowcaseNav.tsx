"use client";

import { useEffect, useState } from "react";

const links = [
  ["why", "Why"],
  ["dataset", "Dataset"],
  ["methodology", "Method"],
  ["accuracy", "Accuracy"],
  ["architecture", "Architecture"],
  ["results", "Results"],
  ["deployment", "Deploy"],
] as const;

export function ShowcaseNav() {
  const [active, setActive] = useState("hero");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible?.target.id) setActive(visible.target.id);
      },
      { rootMargin: "-120px 0px -65% 0px", threshold: [0.1, 0.3, 0.6] }
    );

    for (const [id] of links) {
      const node = document.getElementById(id);
      if (node) observer.observe(node);
    }
    return () => observer.disconnect();
  }, []);

  return (
    <div className="sticky top-[57px] z-40 hidden border-b border-[var(--border)] bg-[var(--background)]/70 backdrop-blur-xl lg:block">
      <div className="mx-auto flex max-w-[1240px] items-center gap-2 px-6 py-2">
        {links.map(([id, label]) => (
          <a
            key={id}
            href={`#${id}`}
            className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
              active === id
                ? "bg-blue-600 text-white"
                : "text-[var(--text-secondary)] hover:bg-[var(--surface)] hover:text-[var(--text-primary)]"
            }`}
          >
            {label}
          </a>
        ))}
      </div>
    </div>
  );
}
