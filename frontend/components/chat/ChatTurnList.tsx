import React from "react";
import { Bot, User, Sparkles, Database, ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { ChatTurn, CandidateMemory } from "@/lib/types";
import { formatScore } from "@/lib/utils";

export interface ChatMessageItem extends ChatTurn {
  id: string;
  candidate_memory?: CandidateMemory | null;
  memory_status?: string | null;
  trust_score?: number | null;
  retrieved_memories?: string[];
  timestamp: string;
}

interface ChatTurnListProps {
  messages: ChatMessageItem[];
  onSelectCandidate?: (message: ChatMessageItem) => void;
}

export const ChatTurnList: React.FC<ChatTurnListProps> = ({
  messages,
  onSelectCandidate,
}) => {
  return (
    <div className="space-y-4">
      {messages.map((msg) => {
        const isUser = msg.role === "user";
        return (
          <div
            key={msg.id}
            className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
          >
            {!isUser && (
              <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0 mt-0.5">
                <Bot className="w-3.5 h-3.5" />
              </div>
            )}

            <div className={`flex flex-col max-w-[80%] space-y-1.5 ${isUser ? "items-end" : "items-start"}`}>
              <div
                className={`px-4 py-3 rounded-xl text-xs leading-relaxed ${
                  isUser
                    ? "bg-blue-600 text-white rounded-br-none shadow-sm"
                    : "bg-slate-950 border border-slate-800 text-slate-200 rounded-bl-none shadow-sm"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {msg.retrieved_memories && msg.retrieved_memories.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-slate-800/80 text-[10px] text-slate-400 space-y-1">
                    <div className="font-semibold text-slate-300 flex items-center gap-1">
                      <Database className="w-3 h-3 text-cyan-400" />
                      Retrieved Verified Context:
                    </div>
                    <ul className="list-disc list-inside space-y-0.5 text-cyan-300/80">
                      {msg.retrieved_memories.map((rm, idx) => (
                        <li key={idx} className="truncate">{rm}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {msg.candidate_memory && (
                <button
                  onClick={() => onSelectCandidate && onSelectCandidate(msg)}
                  className={`flex items-center gap-2 px-2.5 py-1 rounded-md text-[11px] border transition-all text-left ${
                    msg.memory_status === "ACCEPTED"
                      ? "bg-emerald-950/40 border-emerald-800/60 text-emerald-300 hover:bg-emerald-950/70"
                      : "bg-rose-950/40 border-rose-800/60 text-rose-300 hover:bg-rose-950/70"
                  }`}
                >
                  <Sparkles className="w-3 h-3 shrink-0" />
                  <span className="truncate">
                    Candidate: <strong>{msg.candidate_memory.content}</strong>
                  </span>
                  <Badge status={msg.memory_status || "PENDING_ANALYSIS"} size="sm">
                    {msg.memory_status}
                  </Badge>
                  <span className="font-mono text-[10px] text-slate-400">
                    {formatScore(msg.trust_score)}
                  </span>
                  <ChevronRight className="w-3 h-3 ml-auto text-slate-500" />
                </button>
              )}

              <span className="text-[10px] text-slate-500 px-1">{msg.timestamp}</span>
            </div>

            {isUser && (
              <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-0.5">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
