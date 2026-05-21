"use client";

import { useEffect, useState } from "react";
import { MessageSquare, Plus, Hash } from "lucide-react";
import { getThreads } from "@/lib/api";
import { motion } from "framer-motion";

interface SidebarProps {
  activeThread: string;
  onSelectThread: (id: string) => void;
  onNewChat: () => void;
}

export default function Sidebar({ activeThread, onSelectThread, onNewChat }: SidebarProps) {
  const [threads, setThreads] = useState<string[]>([]);

  useEffect(() => {
    refreshThreads();
  }, [activeThread]);

  const refreshThreads = async () => {
    const data = await getThreads();
    setThreads(data.threads || []);
  };

  return (
    <div className="w-80 h-full bg-slate-900 border-r border-slate-700/50 flex flex-col p-4">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
          Agentic Chat
        </h1>
      </div>

      <button
        onClick={onNewChat}
        className="flex items-center gap-2 w-full py-3 px-4 rounded-xl bg-cyan-600 hover:bg-cyan-500 transition-colors font-medium mb-8 shadow-lg shadow-cyan-900/20"
      >
        <Plus className="w-5 h-5" />
        Start New Chat
      </button>

      <div className="flex-1 overflow-y-auto space-y-2">
        <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 px-2">
          Your Conversations
        </p>
        {threads.map((tid) => (
          <motion.button
            key={tid}
            whileHover={{ x: 4 }}
            onClick={() => onSelectThread(tid)}
            className={`flex items-center gap-3 w-full py-3 px-4 rounded-xl transition-all ${
              activeThread === tid
                ? "glass-cyan border-cyan-500/50 text-cyan-400"
                : "hover:bg-slate-800/50 text-slate-400"
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span className="text-sm font-medium truncate">Thread: {tid}</span>
          </motion.button>
        ))}
        {threads.length === 0 && (
          <p className="text-sm text-slate-600 px-2 italic">No conversations yet.</p>
        )}
      </div>

      <div className="pt-4 border-t border-slate-800 mt-4">
        <div className="flex items-center gap-2 px-2 text-slate-500 text-sm">
          <Hash className="w-4 h-4" />
          <span>v1.0.0 Stable</span>
        </div>
      </div>
    </div>
  );
}
