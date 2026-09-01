import React from "react";
import { AttackScenario } from "@/lib/types";

interface ScenarioCardProps {
  scenario: AttackScenario;
  isSelected: boolean;
  onSelect: (scenario: AttackScenario) => void;
}

export const ScenarioCard: React.FC<ScenarioCardProps> = ({
  scenario,
  isSelected,
  onSelect,
}) => {
  return (
    <div
      onClick={() => onSelect(scenario)}
      className={`p-3 rounded-lg border cursor-pointer transition-all text-xs ${
        isSelected
          ? "bg-blue-950/40 border-blue-500 shadow-sm"
          : "bg-slate-950/60 border-slate-800/80 hover:bg-slate-900"
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold text-slate-100">{scenario.name}</span>
        <div className="flex items-center gap-1.5">
          <span
            className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${
              scenario.severity === "CRITICAL"
                ? "bg-rose-950 text-rose-400 border-rose-800"
                : scenario.severity === "HIGH"
                ? "bg-amber-950 text-amber-400 border-amber-800"
                : "bg-slate-900 text-slate-400 border-slate-800"
            }`}
          >
            {scenario.severity}
          </span>
          {!scenario.is_active && (
            <span className="text-[10px] text-slate-500 font-mono">(Placeholder)</span>
          )}
        </div>
      </div>
      <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
        {scenario.description}
      </p>
    </div>
  );
};
