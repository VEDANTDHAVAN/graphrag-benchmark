import { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
};

function cx(...parts: Array<string | undefined | false>) {
  return parts.filter(Boolean).join(" ");
}

export function Button({ className, variant = "secondary", ...props }: Props) {
  const base =
    "inline-flex h-10 items-center justify-center rounded-lg border px-4 text-sm font-semibold shadow-sm transition-colors disabled:cursor-not-allowed disabled:opacity-60";

  const styles =
    variant === "primary"
      ? "border-blue-600 bg-blue-600 text-white hover:bg-blue-700 hover:border-blue-700"
      : "border-[var(--border)] bg-[var(--surface)] text-[var(--text-primary)] hover:bg-white/60 dark:hover:bg-white/5";

  return <button className={cx(base, styles, className)} {...props} />;
}

