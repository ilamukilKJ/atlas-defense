import React from "react";
import { cn, getStatusBadgeClasses } from "@/lib/utils";
import { MemoryStatus } from "@/lib/types";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "info" | "neutral" | "warning" | "danger" | "success";
  status?: MemoryStatus | string;
  className?: string;
  size?: "sm" | "md";
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "neutral",
  status,
  className,
  size = "md",
}) => {
  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-xs";

  if (status) {
    return (
      <span
        className={cn(
          "inline-flex items-center font-semibold rounded-md border ring-1",
          sizeClasses,
          getStatusBadgeClasses(status),
          className
        )}
      >
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full mr-1.5",
            status === "ACCEPTED" ? "bg-emerald-400" : "bg-rose-400"
          )}
        />
        {children}
      </span>
    );
  }

  const variantStyles = {
    info: "bg-blue-950/60 text-blue-400 border-blue-800/60 ring-blue-500/20",
    neutral: "bg-slate-800/80 text-slate-300 border-slate-700/60 ring-slate-500/10",
    warning: "bg-amber-950/60 text-amber-400 border-amber-800/60 ring-amber-500/20",
    danger: "bg-rose-950/60 text-rose-400 border-rose-800/60 ring-rose-500/20",
    success: "bg-emerald-950/60 text-emerald-400 border-emerald-800/60 ring-emerald-500/20",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-md border ring-1",
        sizeClasses,
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
};
