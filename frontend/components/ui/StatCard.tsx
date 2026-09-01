import React from "react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: "up" | "down" | "neutral";
  trendLabel?: string;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  className,
}) => {
  return (
    <div
      className={cn(
        "p-4 rounded-xl border border-slate-800 bg-slate-900/90 text-slate-100 flex flex-col justify-between shadow-sm",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        {icon && <div className="p-2 rounded-lg bg-slate-800/80 text-blue-400">{icon}</div>}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold tracking-tight text-slate-100">{value}</div>
        {subtitle && <p className="text-xs text-slate-400 mt-1 leading-normal">{subtitle}</p>}
      </div>
    </div>
  );
};
