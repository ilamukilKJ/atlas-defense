"use client";

import React, { useEffect, useState } from "react";
import {
  Database,
  Search,
  CheckCircle,
  XCircle,
  Filter,
  Trash2,
  RefreshCw,
  Info,
  ChevronDown,
  ChevronUp,
  Activity,
  Layers
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { SignalBar } from "@/components/ui/SignalBar";
import { TrustGauge } from "@/components/ui/TrustGauge";
import { api } from "@/lib/api";
import { MemoryItem, MemoryStatus } from "@/lib/types";
import { formatDate, formatScore, getScoreTextColor } from "@/lib/utils";

export default function MemoryMonitorPage() {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [filteredStatus, setFilteredStatus] = useState<MemoryStatus | "ALL">("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [selectedMemory, setSelectedMemory] = useState<MemoryItem | null>(null);

  const loadMemories = async () => {
    setLoading(true);
    try {
      const statusParam = filteredStatus === "ALL" ? undefined : filteredStatus;
      const res = await api.getMemories(statusParam, searchQuery);
      setMemories(res.memories);
      if (selectedMemory) {
        const updated = res.memories.find((m) => m.id === selectedMemory.id);
        setSelectedMemory(updated || null);
      }
    } catch (err) {
      console.error("Failed to load memories:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemories();
  }, [filteredStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadMemories();
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to delete memory '${id}'?`)) return;
    try {
      await api.deleteMemory(id);
      setMemories((prev) => prev.filter((m) => m.id !== id));
      if (selectedMemory?.id === id) setSelectedMemory(null);
    } catch (err) {
      console.error("Failed to delete memory:", err);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Memory Monitor & Persistent Storage
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Inspect persistent long-term vector memories and quarantined adversarial statements
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadMemories} loading={loading}>
            <RefreshCw className="w-3.5 h-3.5 mr-1" /> Refresh
          </Button>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
        {/* Status Filter Tabs */}
        <div className="flex items-center space-x-1 p-1 bg-slate-950 rounded-lg border border-slate-800/80">
          {(["ALL", "ACCEPTED", "QUARANTINED"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilteredStatus(tab)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                filteredStatus === tab
                  ? "bg-slate-800 text-slate-100 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {tab === "ALL" && "All Records"}
              {tab === "ACCEPTED" && (
                <span className="flex items-center gap-1.5">
                  <CheckCircle className="w-3 h-3 text-emerald-400" /> Accepted
                </span>
              )}
              {tab === "QUARANTINED" && (
                <span className="flex items-center gap-1.5">
                  <XCircle className="w-3 h-3 text-rose-400" /> Quarantined
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="flex gap-2 flex-1 max-w-md">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search memory text, category, or origin..."
              className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <Button type="submit" size="sm" variant="secondary">
            Search
          </Button>
        </form>
      </div>

      {/* Main Content: Table + Side Detail Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Memory Table */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Stored Memories ({memories.length})</CardTitle>
            <CardDescription>
              Click on any row to inspect its full six-signal ATLAS diagnostic breakdown
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="py-12 text-center text-slate-500 text-xs flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-blue-400" />
                Loading memory records from vector store...
              </div>
            ) : memories.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-xs space-y-2">
                <Info className="w-8 h-8 text-slate-600 mx-auto stroke-[1.5]" />
                <p>No memory items found matching the current filter.</p>
              </div>
            ) : (
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
                      const isSelected = selectedMemory?.id === mem.id;
                      return (
                        <tr
                          key={mem.id}
                          onClick={() => setSelectedMemory(mem)}
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
                              onClick={(e) => handleDelete(mem.id, e)}
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
            )}
          </CardContent>
        </Card>

        {/* Selected Memory Detail Drawer */}
        <Card className="h-fit">
          <CardHeader>
            <CardTitle>
              <Activity className="w-4 h-4 text-blue-400" />
              Memory Trust Analysis
            </CardTitle>
            <CardDescription>
              Deep inspection of selected memory item
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedMemory ? (
              <div className="space-y-4">
                {/* Memory Full Text */}
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
                  <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
                    <span>Memory ID: {selectedMemory.id}</span>
                    <span>{formatDate(selectedMemory.timestamp)}</span>
                  </div>
                  <p className="text-xs font-medium text-slate-200 mt-1 leading-relaxed">
                    "{selectedMemory.content}"
                  </p>
                  <div className="flex items-center gap-2 pt-2">
                    <Badge status={selectedMemory.status}>{selectedMemory.status}</Badge>
                    <span className="text-[10px] text-slate-400">
                      Category: <strong>{selectedMemory.category}</strong>
                    </span>
                  </div>
                </div>

                {/* Trust Gauge */}
                <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex justify-center">
                  <TrustGauge score={selectedMemory.trust_score} threshold={0.65} size="md" />
                </div>

                {/* Decision Reason */}
                {selectedMemory.decision_reason && (
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 leading-relaxed">
                    <strong className="text-slate-200 block mb-0.5">Decision Note:</strong>
                    {selectedMemory.decision_reason}
                  </div>
                )}

                {/* Signals Breakdown */}
                {selectedMemory.signals && (
                  <div className="space-y-2">
                    <div className="text-xs font-semibold text-slate-300">
                      Six ATLAS Signal Breakdown:
                    </div>
                    <SignalBar
                      name="1. Semantic Relevance"
                      score={selectedMemory.signals.semantic_relevance}
                      weight={0.20}
                    />
                    <SignalBar
                      name="2. Embedding Anomaly"
                      score={selectedMemory.signals.embedding_anomaly}
                      weight={0.20}
                    />
                    <SignalBar
                      name="3. Historical Consistency"
                      score={selectedMemory.signals.historical_consistency}
                      weight={0.20}
                    />
                    <SignalBar
                      name="4. Behavioral Consistency"
                      score={selectedMemory.signals.behavioral_consistency}
                      weight={0.15}
                    />
                    <SignalBar
                      name="5. Source Reliability"
                      score={selectedMemory.signals.source_reliability}
                      weight={0.15}
                    />
                    <SignalBar
                      name="6. Temporal Trust"
                      score={selectedMemory.signals.temporal_trust}
                      weight={0.10}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="py-12 text-center text-slate-500 text-xs space-y-2">
                <Layers className="w-8 h-8 text-slate-600 mx-auto stroke-[1.5]" />
                <p>Select any memory from the table to inspect its full ATLAS trust parameters.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
