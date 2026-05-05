import { ReactNode } from "react";

type Props = {
  children: ReactNode;
  className?: string;
};

function cx(...parts: Array<string | undefined | false>) {
  return parts.filter(Boolean).join(" ");
}

export function Card({ children, className }: Props) {
  return (
    <section
      className={cx(
        "rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-sm",
        className
      )}
    >
      {children}
    </section>
  );
}

export function CardHeader({ children, className }: Props) {
  return (
    <header
      className={cx(
        "flex items-start justify-between gap-4 border-b border-[var(--border)] px-5 py-4",
        className
      )}
    >
      {children}
    </header>
  );
}

export function CardTitle({ children, className }: Props) {
  return (
    <h2 className={cx("text-sm font-semibold text-[var(--text-primary)]", className)}>
      {children}
    </h2>
  );
}

export function CardDescription({ children, className }: Props) {
  return (
    <p className={cx("mt-1 text-xs text-[var(--text-secondary)]", className)}>
      {children}
    </p>
  );
}

export function CardContent({ children, className }: Props) {
  return <div className={cx("px-5 py-4", className)}>{children}</div>;
}

