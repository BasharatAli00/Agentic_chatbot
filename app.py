import streamlit as st
import uuid
from datetime import datetime
from backend.graph import run_graph
from ui.styles import GLOBAL_CSS
from ui.components import render_thinking, render_message

st.set_page_config(
    page_title="DeepSeek Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ──────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Session State Init ──────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sessions" not in st.session_state:
    st.session_state.sessions = {}   # { thread_id: [messages] }
if "thinking" not in st.session_state:
    st.session_state.thinking = False

# ── SIDEBAR ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 DeepSeek Agent")
    st.divider()

    if st.button("＋  New Chat", use_container_width=True):
        # Save current session before switching
        if st.session_state.messages:
            st.session_state.sessions[st.session_state.thread_id] = (
                st.session_state.messages.copy()
            )
        st.session_state.thread_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.rerun()

    st.markdown("**Recent Sessions**")
    for tid, msgs in reversed(list(st.session_state.sessions.items())):
        preview = msgs[0]["content"][:30] + "..." if msgs else "Empty"
        is_active = tid == st.session_state.thread_id
        if st.button(f"💬 {preview}", key=f"sess_{tid}", use_container_width=True):
            # Save current
            st.session_state.sessions[st.session_state.thread_id] = (
                st.session_state.messages.copy()
            )
            # Switch
            st.session_state.thread_id = tid
            st.session_state.messages = st.session_state.sessions[tid].copy()
            st.rerun()

    st.divider()
    st.markdown("**Settings**")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    max_tokens = st.number_input("Max Tokens", 256, 4096, 1024, 128)
    st.caption(f"Model: `deepseek-chat`")

# ── HEADER ───────────────────────────────────────────────
col1, col2, col3 = st.columns([4, 2, 1])
with col1:
    st.markdown("## 🤖 DeepSeek Agentic Chat")
with col2:
    st.markdown(
        f'<div class="thread-badge">Thread: {st.session_state.thread_id}</div>',
        unsafe_allow_html=True,
    )
with col3:
    if st.button("Clear 🗑️"):
        st.session_state.messages = []
        st.rerun()

st.divider()

# ── CHAT MESSAGES ────────────────────────────────────────
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            render_message(msg["content"], msg["role"])



# ── INPUT BAR ────────────────────────────────────────────
if prompt := st.chat_input("Ask anything… (Shift+Enter for new line)"):
    # 1. Append user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().strftime("%H:%M"),
    })
    st.session_state.thinking = True
    st.rerun()

# ── LLM CALL (triggered after rerun when thinking=True) ──
if st.session_state.thinking:
    last_user_msg = next(
        (m for m in reversed(st.session_state.messages) if m["role"] == "user"),
        None
    )
    if last_user_msg:
        try:
            with st.chat_message("assistant"):
                # Use st.write_stream to handle the generator and display tokens in real-time
                response_generator = run_graph(
                    message=last_user_msg["content"],
                    thread_id=st.session_state.thread_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                full_response = st.write_stream(response_generator)
                
            # Store the final string, NOT the generator
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
        except Exception as e:
            import traceback
            st.error(f"Error: {str(e)}")
            print(traceback.format_exc())
            
    st.session_state.thinking = False
    st.rerun()
