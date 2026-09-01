import React from "react";
import { RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface SignalWeightEditorProps {
  weights: Record<string, number>;
  onChange: (key: string, value: number) => void;
  onReset: () => void;
}

export const SignalWeightEditor: React.FC<SignalWeightEditorProps> = ({
  weights,
  onChange,
  onReset,
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300">
          Normalized Sensitivity Weights:
        </span>
        <Button variant="ghost" size="sm" onClick={onReset}>
          <RotateCcw className="w-3 h-3 mr-1" /> Reset Defaults
        </Button>
      </div>

      {Object.entries(weights).map(([key, val]) => (
        <div key={key} className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="font-medium text-slate-300 capitalize">
              {key.replace("_", " ")}
            </span>
            <span className="font-mono text-slate-400 font-bold">
              {(val * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0.0"
            max="0.5"
            step="0.05"
            value={val}
            onChange={(e) => onChange(key, parseFloat(e.target.value))}
            className="w-full accent-blue-500 bg-slate-800 h-1.5 rounded-lg cursor-pointer"
          />
        </div>
      ))}
    </div>
  );
};
