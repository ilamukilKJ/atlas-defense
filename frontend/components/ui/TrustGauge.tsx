import React from "react";
import { cn } from "@/lib/utils";

interface TrustGaugeProps {
  score: number; // 0.0 to 1.0
  threshold?: number;
  size?: "sm" | "md" | "lg";
  className?: string;
  showDetails?: boolean;
}

export const TrustGauge: React.FC<TrustGaugeProps> = ({
  score,
  threshold = 0.65,
  size = "md",
  className,
  showDetails = true,
}) => {
  const clampedScore = Math.max(0, Math.min(1, score || 0));
  const percentage = Math.round(clampedScore * 100);
  const isAccepted = clampedScore >= threshold;

  const dimensions = {
    sm: { radius: 36, stroke: 6, width: 90, height: 90, textSize: "text-lg", subSize: "text-[10px]" },
    md: { radius: 52, stroke: 8, width: 130, height: 130, textSize: "text-2xl", subSize: "text-xs" },
    lg: { radius: 72, stroke: 10, width: 180, height: 180, textSize: "text-4xl", subSize: "text-sm" },
  }[size];

  const circumference = 2 * Math.PI * dimensions.radius;
  const strokeDashoffset = circumference - clampedScore * circumference;

  const colorClass = isAccepted
    ? "text-emerald-500"
    : clampedScore >= 0.50
    ? "text-amber-500"
    : "text-rose-500";

  const strokeColor = isAccepted
    ? "#10b981"
    : clampedScore >= 0.50
    ? "#f59e0b"
    : "#ef4444";

  return (
    <div className={cn("flex flex-col items-center justify-center relative", className)}>
      <div className="relative" style={{ width: dimensions.width, height: dimensions.height }}>
        <svg
          className="transform -rotate-90 origin-center"
          width={dimensions.width}
          height={dimensions.height}
        >
          {/* Background circle */}
          <circle
            cx={dimensions.width / 2}
            cy={dimensions.height / 2}
            r={dimensions.radius}
            stroke="#1e293b"
            strokeWidth={dimensions.stroke}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={dimensions.width / 2}
            cy={dimensions.height / 2}
            r={dimensions.radius}
            stroke={strokeColor}
            strokeWidth={dimensions.stroke}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-700 ease-out"
          />
        </svg>

        {/* Center score label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className={cn("font-bold tracking-tight", dimensions.textSize, colorClass)}>
            {percentage}%
          </span>
          <span className={cn("text-slate-400 font-mono tracking-wider", dimensions.subSize)}>
            TRUST
          </span>
        </div>
      </div>

      {showDetails && (
        <div className="mt-2 text-center">
          <span
            className={cn(
              "text-xs font-semibold px-2 py-0.5 rounded-full border",
              isAccepted
                ? "bg-emerald-950/70 text-emerald-400 border-emerald-800/60"
                : "bg-rose-950/70 text-rose-400 border-rose-800/60"
            )}
          >
            {isAccepted ? "ACCEPTED" : "QUARANTINED"}
          </span>
          <p className="text-[11px] text-slate-500 mt-1">
            Threshold: {(threshold * 100).toFixed(0)}%
          </p>
        </div>
      )}
    </div>
  );
};
