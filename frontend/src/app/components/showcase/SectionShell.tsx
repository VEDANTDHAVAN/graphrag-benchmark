import { MotionSection } from "./MotionSection";

export function SectionShell({
  id,
  eyebrow,
  title,
  description,
  children,
}: {
  id: string;
  eyebrow: string;
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <MotionSection id={id} className="mx-auto w-full max-w-[1240px] px-4 py-16 sm:px-6 lg:py-20">
      <div className="mb-8 max-w-3xl">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-600 dark:text-blue-300">
          {eyebrow}
        </div>
        <h2 className="mt-3 text-2xl font-semibold tracking-tight text-[var(--text-primary)] sm:text-3xl">
          {title}
        </h2>
        {description && (
          <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
            {description}
          </p>
        )}
      </div>
      {children}
    </MotionSection>
  );
}
