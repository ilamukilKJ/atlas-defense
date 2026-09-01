import React from "react";
import { cn, getScoreTextColor, getScoreBgColor } from "@/lib/utils";

interface SignalBarProps {
  name: string;
  score: number; // 0.0 to 1.0
  weight?: number;
  description?: string;
  icon?: React.ReactNode;
  className?: string;
}

export const SignalBar: React.FC<SignalBarProps> = ({
  name,
  score,
  weight,
  description,
  icon,
  className,
}) => {
  const percentage = Math.round(score * 100);

  return (
    <div className={cn("flex flex-col space-y-1.5 p-3 rounded-lg bg-slate-900/60 border border-slate-800/80", className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {icon && <span className="text-slate-400">{icon}</span>}
          <div>
            <div className="text-xs font-semibold text-slate-200">{name}</div>
            {description && <div className="text-[10px] text-slate-400">{description}</div>}
          </div>
        </div>
        <div className="text-right">
          <span className={cn("text-xs font-bold font-mono", getScoreTextColor(score))}>
            {percentage}%
          </span>
          {weight !== undefined && (
            <span className="text-[10px] text-slate-500 block">
              w = {(weight * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>

      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={cn("h-full transition-all duration-500 rounded-full", getScoreBgColor(score))}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
