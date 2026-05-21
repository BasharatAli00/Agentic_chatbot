"use client";

import { useState, useEffect, useRef } from "react";
import Sidebar from "@/components/Sidebar";
import MessageBubble from "@/components/MessageBubble";
import ToolBadge from "@/components/ToolBadge";
import { streamChat, getHistory, ChatEvent } from "@/lib/api";
import { Send, Sparkles, Loader2 } from "lucide-react";
import { v4 as uuidv4 } from "uuid";

export default function Home() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [activeTools, setActiveTools] = useState<string[]>([]);
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tid = localStorage.getItem("thread_id") || uuidv4().slice(0, 8);
    setThreadId(tid);
    localStorage.setItem("thread_id", tid);
    loadHistory(tid);
  }, []);

  const loadHistory = async (tid: string) => {
    const history = await getHistory(tid);
    setMessages(history);
  };

  const handleSelectThread = (tid: string) => {
    setThreadId(tid);
    localStorage.setItem("thread_id", tid);
    loadHistory(tid);
  };

  const handleNewChat = () => {
    const tid = uuidv4().slice(0, 8);
    setThreadId(tid);
    localStorage.setItem("thread_id", tid);
    setMessages([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isThinking) return;

    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsThinking(true);
    setActiveTools([]);

    try {
      let fullResponse = "";
      const stream = streamChat(input, threadId);
      
      // Add empty assistant message to populate
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      for await (const event of stream) {
        if (event.type === "text" && event.content) {
          fullResponse += event.content;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = { role: "assistant", content: fullResponse };
            return updated;
          });
        } else if (event.type === "tool_call") {
          setActiveTools(event.names || []);
        } else if (event.type === "tool") {
          // Clear tools after execution if needed or keep for duration
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsThinking(false);
      setActiveTools([]);
    }
  };

  useEffect(() => {
    if (messages.length > 0 || activeTools.length > 0) {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, activeTools]);

  return (
    <main className="flex h-screen bg-slate-950 overflow-hidden">
      <Sidebar 
        activeThread={threadId} 
        onSelectThread={handleSelectThread} 
        onNewChat={handleNewChat} 
      />

      <div className="flex-1 flex flex-col min-h-0 relative">
        {/* Background Gradients */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-cyan-500/5 blur-[120px] rounded-full -mr-64 -mt-64 pointer-events-none" />
        
        {/* Header - Fixed Height */}
        <header className="flex-none h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur-xl flex items-center px-8 z-30">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm font-semibold text-slate-200">
              Active Thread: <span className="text-cyan-400 font-mono">{threadId || "---"}</span>
            </span>
          </div>
        </header>

        {/* Chat Area - Scrollable */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-4 z-10 custom-scrollbar">
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 && !isThinking && (
              <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
                <div className="w-20 h-20 bg-cyan-500/10 rounded-3xl flex items-center justify-center border border-cyan-500/20 mb-4">
                  <Sparkles className="w-10 h-10 text-cyan-400" />
                </div>
                <h2 className="text-3xl font-bold text-white">How can I help you today?</h2>
                <p className="text-slate-400 max-w-sm">Ask me about search, math, or any general questions.</p>
              </div>
            )}
            
            {messages.map((m, i) => (
              <MessageBubble key={i} message={m} />
            ))}

            {activeTools.length > 0 && (
              <div className="flex flex-col gap-2">
                <ToolBadge names={activeTools} />
              </div>
            )}
            
            {isThinking && messages[messages.length-1]?.content === "" && (
              <div className="flex items-center gap-2 text-slate-500 text-sm italic ml-14">
                <Loader2 className="w-4 h-4 animate-spin" />
                AI is processing...
              </div>
            )}
            
            <div ref={scrollRef} className="h-4" />
          </div>
        </div>

        {/* Input Bar - Fixed at Bottom */}
        <footer className="flex-none p-6 md:p-8 bg-gradient-to-t from-slate-950 via-slate-950 to-transparent z-20">
          <div className="max-w-4xl mx-auto relative">
            <form onSubmit={handleSubmit} className="relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me anything..."
                className="w-full bg-slate-900/80 border border-slate-700/50 rounded-2xl py-4 pl-6 pr-24 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 text-white placeholder-slate-500 backdrop-blur-md shadow-2xl transition-all"
              />
              <div className="absolute right-2 top-2 bottom-2 flex items-center gap-2">
                <button
                  type="submit"
                  disabled={!input.trim() || isThinking}
                  className="h-full px-6 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:bg-slate-700 text-white rounded-xl transition-all flex items-center gap-2"
                >
                  <span className="hidden sm:inline font-medium">Send</span>
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </form>
            <p className="text-center text-[10px] text-slate-600 mt-4 uppercase tracking-[0.2em] font-bold">
              Powered by DeepSeek AI & Agentic LangGraph
            </p>
          </div>
        </footer>
      </div>
    </main>
  );
}
