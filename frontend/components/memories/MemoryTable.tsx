import React from "react";
import { Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { MemoryItem } from "@/lib/types";
import { formatScore, getScoreTextColor } from "@/lib/utils";

interface MemoryTableProps {
  memories: MemoryItem[];
  selectedId?: string | null;
  onSelect: (mem: MemoryItem) => void;
  onDelete: (id: string, e: React.MouseEvent) => void;
}

export const MemoryTable: React.FC<MemoryTableProps> = ({
  memories,
  selectedId,
  onSelect,
  onDelete,
}) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead className="text-[11px] text-slate-400 border-b border-slate-800 uppercase tracking-wider font-semibold">
          <tr>
            <th className="pb-3 font-medium">Content</th>
            <th className="pb-3 font-medium">Status</th>
            <th className="pb-3 font-medium">Trust</th>
            <th className="pb-3 font-medium">Anomaly</th>
            <th className="pb-3 font-medium">Source</th>
            <th className="pb-3 font-medium text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 font-sans text-xs">
          {memories.map((mem) => {
            const isSelected = selectedId === mem.id;
            return (
              <tr
                key={mem.id}
                onClick={() => onSelect(mem)}
                className={`cursor-pointer transition-colors ${
                  isSelected
                    ? "bg-blue-950/30 border-l-2 border-l-blue-500"
                    : "hover:bg-slate-900/50"
                }`}
              >
                <td className="py-3 pr-4 max-w-xs font-medium text-slate-200 truncate">
                  {mem.content}
                </td>
                <td className="py-3 pr-4">
                  <Badge status={mem.status} size="sm">
                    {mem.status}
                  </Badge>
                </td>
                <td className="py-3 pr-4 font-mono font-bold">
                  <span className={getScoreTextColor(mem.trust_score)}>
                    {formatScore(mem.trust_score)}
                  </span>
                </td>
                <td className="py-3 pr-4 font-mono text-[11px] text-slate-400">
                  {formatScore(mem.anomaly_score)}
                </td>
                <td className="py-3 pr-4 text-slate-400 text-[11px]">
                  <span className="px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[10px]">
                    {mem.source}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <button
                    onClick={(e) => onDelete(mem.id, e)}
                    className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                    title="Delete Memory"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
