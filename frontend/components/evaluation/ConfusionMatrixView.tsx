import React from "react";
import { ConfusionMatrix } from "@/lib/types";
import { formatScore } from "@/lib/utils";

interface ConfusionMatrixViewProps {
  matrix: ConfusionMatrix;
  totalSamples: number;
  falsePositiveRate: number;
}

export const ConfusionMatrixView: React.FC<ConfusionMatrixViewProps> = ({
  matrix,
  totalSamples,
  falsePositiveRate,
}) => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        {/* True Positive */}
        <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-800/60">
          <div className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">
            True Positive (TP)
          </div>
          <div className="text-2xl font-bold text-emerald-300 mt-1">
            {matrix.true_positives}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Malicious attacks correctly <strong>QUARANTINED</strong>
          </div>
        </div>

        {/* False Positive */}
        <div className="p-3.5 rounded-lg bg-amber-950/30 border border-amber-800/60">
          <div className="text-[10px] text-amber-400 font-bold uppercase tracking-wider">
            False Positive (FP)
          </div>
          <div className="text-2xl font-bold text-amber-300 mt-1">
            {matrix.false_positives}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Benign memories incorrectly <strong>QUARANTINED</strong>
          </div>
        </div>

        {/* False Negative */}
        <div className="p-3.5 rounded-lg bg-rose-950/30 border border-rose-800/60">
          <div className="text-[10px] text-rose-400 font-bold uppercase tracking-wider">
            False Negative (FN)
          </div>
          <div className="text-2xl font-bold text-rose-300 mt-1">
            {matrix.false_negatives}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Malicious attacks erroneously <strong>ACCEPTED</strong>
          </div>
        </div>

        {/* True Negative */}
        <div className="p-3.5 rounded-lg bg-blue-950/30 border border-blue-800/60">
          <div className="text-[10px] text-blue-400 font-bold uppercase tracking-wider">
            True Negative (TN)
          </div>
          <div className="text-2xl font-bold text-blue-300 mt-1">
            {matrix.true_negatives}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Benign memories correctly <strong>ACCEPTED</strong>
          </div>
        </div>
      </div>

      <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
        <span>Total Evaluated Samples: <strong>{totalSamples}</strong></span>
        <span>False Positive Rate (FPR): <strong className="text-slate-200">{formatScore(falsePositiveRate)}</strong></span>
      </div>
    </div>
  );
};
