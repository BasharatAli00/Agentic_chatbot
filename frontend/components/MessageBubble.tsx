"use client";

import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { motion } from "framer-motion";
import { User, Bot } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 20 : -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        "flex w-full mb-6 gap-4",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <div className={cn(
        "w-10 h-10 rounded-full flex items-center justify-center shrink-0 border",
        isUser ? "bg-cyan-500/20 border-cyan-500/50" : "bg-purple-500/20 border-purple-500/50"
      )}>
        {isUser ? <User className="w-6 h-6 text-cyan-400" /> : <Bot className="w-6 h-6 text-purple-400" />}
      </div>

      <div className={cn(
        "max-w-[80%] rounded-2xl p-4 shadow-xl",
        isUser 
          ? "bg-gradient-to-br from-cyan-900/40 to-slate-900/60 border border-cyan-500/30 rounded-tr-none" 
          : "bg-slate-800/60 border border-purple-500/20 rounded-tl-none"
      )}>
<div className="prose prose-invert max-w-none text-slate-200">
  <ReactMarkdown
    components={{
      code({ node, className, children, ...props }: any) {
        const match = /language-(\w+)/.exec(className || "");
        return match ? (
          <SyntaxHighlighter
            style={atomDark}
            language={match[1]}
            PreTag="div"
            {...props}
          >
            {String(children).replace(/\n$/, "")}
          </SyntaxHighlighter>
        ) : (
          <code className={className} {...props}>
            {children}
          </code>
        );
      },
    }}
  >
    {message.content}
  </ReactMarkdown>
</div>
      </div>
    </motion.div>
  );
}
