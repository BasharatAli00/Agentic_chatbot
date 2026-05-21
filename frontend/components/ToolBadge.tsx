"use client";

import { Search } from "lucide-react";
import { motion } from "framer-motion";

interface ToolBadgeProps {
  names: string[];
}

export default function ToolBadge({ names }: ToolBadgeProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-cyan flex items-center gap-3 px-4 py-3 rounded-xl my-3 relative overflow-hidden"
    >
      <motion.div
        animate={{ rotate: [0, 15, -15, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
      >
        <Search className="w-5 h-5 text-cyan-400" />
      </motion.div>
      <p className="text-sm text-cyan-400 font-medium">
        Agent is searching with <span className="font-bold">{names.join(", ")}</span>...
      </p>
      
      {/* Animated progress bar at bottom */}
      <motion.div 
        className="absolute bottom-0 left-0 h-[2px] bg-cyan-400"
        initial={{ width: "0%", left: "0%" }}
        animate={{ width: ["0%", "100%", "0%"], left: ["0%", "0%", "100%"] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      />
    </motion.div>
  );
}
