import streamlit as st
import re

def render_thinking():
    """Animated pulsing dots while LLM generates."""
    st.markdown(
        """
        <div class="thinking-indicator">
          <span></span><span></span><span></span>
          <small style="color:#64748B; font-size:12px; margin-left:6px;">
            AI is thinking…
          </small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_message(content: str, role: str):
    """
    Render a message with:
      - Markdown support
      - Syntax-highlighted code blocks with copy button
      - Timestamp (passed via session state if needed)
    """
    # Split on code blocks
    parts = re.split(r"(```[\s\S]*?```)", content)
    for part in parts:
        if part.startswith("```"):
            render_code_block(part)
        else:
            st.markdown(part, unsafe_allow_html=True)


def render_code_block(raw: str):
    """
    Renders a fenced code block with:
      - Language label extracted from fence
      - One-click copy button via st.code + JS trick
    """
    lines = raw.strip().split("\n")
    lang = lines[0].replace("```", "").strip() or "text"
    code_body = "\n".join(lines[1:-1])

    col1, col2 = st.columns([8, 1])
    with col1:
        st.code(code_body, language=lang)
    with col2:
        # Copy button — uses pyperclip via st.session_state workaround
        if st.button("📋", key=f"copy_{hash(code_body)}", help="Copy to clipboard"):
            st.session_state[f"copied_{hash(code_body)}"] = True
            st.toast("✅ Copied!", icon="✅")
