GLOBAL_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
  background-color: #0F172A !important;
  font-family: 'Outfit', sans-serif;
  color: #F1F5F9;
}

/* ── Header Glassmorphism ── */
[data-testid="stHeader"] {
  background: rgba(15, 23, 42, 0.7) !important;
  backdrop-filter: blur(12px) !important;
  border-bottom: 1px solid rgba(51, 65, 85, 0.6);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #1E293B !important;
  border-right: 1px solid #334155;
}
[data-testid="stSidebar"] .block-container { padding: 1rem; }

/* ── Input Area Glassmorphism ── */
.stChatInputContainer, [data-testid="stChatInput"] {
  background: rgba(30, 41, 59, 0.85) !important;
  backdrop-filter: blur(16px) !important;
  border: 1px solid rgba(34, 211, 238, 0.25) !important;
  border-radius: 14px !important;
  padding: 0.5rem !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: #F1F5F9 !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 15px !important;
  resize: none !important;
  min-height: 44px !important;
  max-height: 180px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #64748B !important; }

/* ── USER Message Bubble ── */
[data-testid="stChatMessage"][data-role="user"] {
  background: linear-gradient(135deg, rgba(34,211,238,0.15), rgba(34,211,238,0.05)) !important;
  border: 1px solid rgba(34, 211, 238, 0.3) !important;
  border-radius: 16px 4px 16px 16px !important;
  margin-left: auto !important;
  margin-right: 0 !important;
  max-width: 75% !important;
  padding: 12px 16px !important;
}

/* ── AI Message Bubble ── */
[data-testid="stChatMessage"][data-role="assistant"] {
  background: rgba(30, 41, 59, 0.8) !important;
  border: 1px solid rgba(168, 85, 247, 0.25) !important;
  border-radius: 4px 16px 16px 16px !important;
  max-width: 85% !important;
  padding: 14px 16px !important;
}

/* ── Code Blocks ── */
pre, code {
  font-family: 'JetBrains Mono', monospace !important;
  background: #0F172A !important;
  border: 1px solid #334155 !important;
  border-radius: 8px !important;
}
pre { padding: 1rem !important; overflow-x: auto !important; position: relative; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0F172A; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #22D3EE; }

/* ── Thinking Indicator (pulsing dots) ── */
.thinking-indicator {
  display: flex; gap: 6px; align-items: center; padding: 12px 16px;
}
.thinking-indicator span {
  width: 8px; height: 8px; border-radius: 50%;
  background: #A855F7;
  animation: pulse-dot 1.4s ease-in-out infinite;
  box-shadow: 0 0 8px rgba(168, 85, 247, 0.6);
}
.thinking-indicator span:nth-child(2) { animation-delay: 0.2s; }
.thinking-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ── Buttons ── */
.stButton > button {
  background: rgba(34, 211, 238, 0.1) !important;
  border: 1px solid rgba(34, 211, 238, 0.4) !important;
  color: #22D3EE !important;
  border-radius: 8px !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 500 !important;
  transition: all 0.2s ease !important;
}
.stButton > button:hover {
  background: rgba(34, 211, 238, 0.2) !important;
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.3) !important;
}

/* ── Copy Button ── */
.copy-btn {
  position: absolute; top: 8px; right: 8px;
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid #334155;
  color: #64748B;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.copy-btn:hover { color: #22D3EE; border-color: #22D3EE; }

/* ── Thread Badge ── */
.thread-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #64748B;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid #334155;
  border-radius: 20px;
  padding: 2px 10px;
  display: inline-flex; align-items: center; gap: 6px;
}
.thread-badge::before {
  content: '';
  width: 6px; height: 6px; border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 6px #10B981;
}

/* ── Sidebar Session Items ── */
.session-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease;
  margin-bottom: 4px;
  font-size: 13px;
  color: #94A3B8;
}
.session-item:hover { background: #263348; border-color: #334155; color: #F1F5F9; }
.session-item.active { background: rgba(34,211,238,0.08); border-color: rgba(34,211,238,0.3); color: #22D3EE; }
</style>
"""
