import os
import time

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.environ.get("LEXAGENT_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="LexAgent - Legal Research AI",
    page_icon="⚖️",
    layout="wide",
)

# Minimal white/black design with Libra Tech's fonts
# Fonts: Manrope (headings), Inter (body), Geist Mono (code)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    :root {
        --libra-black: #000;
        --libra-white: #fff;
        --libra-light-gray: #f5f5f5;
        --libra-dark-gray: #1a1a1a;
        --libra-border: #e0e0e0;
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #000;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    [data-testid="stAppViewContainer"] {
        background: #fff;
    }

    [data-testid="stAppHeader"] {
        background: #fff;
        border-bottom: 1px solid #e0e0e0;
    }

    .stButton > button {
        background: #000;
        color: #fff;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        font-family: 'Manrope', sans-serif;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #1a1a1a;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .stButton > button:active {
        background: #000;
        transform: scale(0.98);
    }

    .stInfo {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-left: 3px solid #000;
        border-radius: 6px;
        padding: 12px 16px;
    }

    .stSuccess {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
    }

    .stWarning {
        background-color: #fffaf0;
        border: 1px solid #f0e0d0;
        border-radius: 6px;
    }

    .stError {
        background-color: #fff5f5;
        border: 1px solid #ffe0e0;
        border-radius: 6px;
    }

    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        background: #fff;
    }

    .stExpander > button {
        color: #000;
        font-weight: 500;
        font-family: 'Manrope', sans-serif;
    }

    .metric-value {
        color: #000;
        font-weight: 700;
        font-family: 'Manrope', sans-serif;
    }

    .metric-label {
        color: #666;
        font-size: 0.85rem;
    }

    [data-testid="stSidebar"] {
        background: #fff;
        border-right: 1px solid #e0e0e0;
    }

    [data-testid="stSidebarNav"] {
        color: #000;
    }

    .stSidebar .stButton > button {
        width: 100%;
        background: #f5f5f5;
        color: #000;
        border: 1px solid #e0e0e0;
    }

    .stSidebar .stButton > button:hover {
        background: #e8e8e8;
        border-color: #d0d0d0;
    }

    .stDivider {
        background: #e0e0e0;
    }

    code {
        font-family: 'Geist Mono', 'Courier New', monospace;
        background: #f5f5f5;
        color: #000;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.9em;
    }

    a {
        color: #000;
        text-decoration: none;
        border-bottom: 1px solid #e0e0e0;
        transition: border-color 0.2s ease;
    }

    a:hover {
        border-bottom-color: #000;
    }

    .stMarkdown p {
        line-height: 1.6;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar: session management
# ---------------------------------------------------------------------------

st.sidebar.title("⚖️ LexAgent")
st.sidebar.caption("Legal Research AI Agent")

if st.sidebar.button("New Session"):
    st.session_state.pop("session_id", None)
    st.session_state.pop("session_state", None)
    st.rerun()

# Load all sessions for sidebar navigation
try:
    sessions_resp = httpx.get(f"{API_URL}/sessions", timeout=10)
    all_sessions = sessions_resp.json() if sessions_resp.status_code == 200 else []
except Exception:
    all_sessions = []

if all_sessions:
    st.sidebar.subheader("Manage Sessions")
    for s in sorted(all_sessions, key=lambda x: x["created_at"], reverse=True):
        label = f"{s['goal'][:40]}..." if len(s['goal']) > 40 else s['goal']
        badge = "DONE" if not s["is_active"] else f"Step {s['current_step']}"
        col_sel, col_del = st.sidebar.columns([4, 1])
        with col_sel:
            if st.button(f"{label} [{badge}]", key=s["session_id"]):
                st.session_state["session_id"] = s["session_id"]
                st.rerun()
        with col_del:
            if st.button("🗑", key=f"del_{s['session_id']}", help="Delete this session"):
                try:
                    del_resp = httpx.delete(f"{API_URL}/agent/{s['session_id']}", timeout=10)
                    if del_resp.status_code == 204:
                        if st.session_state.get("session_id") == s["session_id"]:
                            st.session_state.pop("session_id", None)
                            st.session_state.pop("session_state", None)
                        st.rerun()
                    else:
                        st.error(f"Delete failed: {del_resp.status_code}")
                except Exception as e:
                    st.error(f"Delete error: {e}")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.title("LexAgent - Legal Research AI")

# --- Goal input (new session) ---
if "session_id" not in st.session_state:
    st.subheader("Start a New Research Session")
    goal = st.text_area(
        "Research Goal",
        placeholder="e.g., Analyze the legal implications of AI-generated evidence in UK criminal proceedings",
        height=120,
    )
    if st.button("Generate Research Plan", type="primary"):
        if not goal.strip():
            st.error("Please enter a research goal.")
        else:
            with st.spinner("Generating research plan..."):
                try:
                    resp = httpx.post(
                        f"{API_URL}/agent/start",
                        json={"goal": goal.strip()},
                        timeout=60,
                    )
                    if resp.status_code == 201:
                        data = resp.json()
                        st.session_state["session_id"] = data["session_id"]
                        st.session_state["session_state"] = data
                        st.rerun()
                    else:
                        st.error(f"API error: {resp.status_code} - {resp.text}")
                except Exception as e:
                    st.error(f"Failed to connect to LexAgent API: {e}")

# --- Session view ---
else:
    session_id = st.session_state["session_id"]

    # Fetch current state
    try:
        resp = httpx.get(f"{API_URL}/agent/{session_id}", timeout=10)
        if resp.status_code == 404:
            st.error("Session not found. It may have been deleted.")
            st.session_state.pop("session_id", None)
            st.stop()
        state = resp.json()
    except Exception as e:
        st.error(f"Failed to load session: {e}")
        st.stop()

    # Header
    st.subheader("Research Goal")
    st.info(state["goal"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Session ID", session_id[:8] + "...")
    col2.metric("Step", f"{state['current_step']} / {len(state['tasks'])}")
    col3.metric("Status", "Complete" if not state["is_active"] else "In Progress")

    st.divider()

    # Task plan display
    st.subheader("Research Plan")
    for i, task in enumerate(state["tasks"]):
        status_icon = {
            "pending": "⬜",
            "in_progress": "🔄",
            "done": "✅",
            "failed": "❌",
        }.get(task["status"], "⬜")

        with st.expander(f"{status_icon} Task {i+1}: {task['title']}", expanded=(task["status"] == "in_progress")):
            st.write(f"**Description:** {task['description']}")
            if task["result"]:
                st.write(f"**Findings:** {task['result']}")
            if task["reflection"]:
                st.write(f"**Reflection:** {task['reflection']}")
            if task["sources"]:
                st.write("**Sources:**")
                for src in task["sources"]:
                    st.write(f"  - {src}")

    st.divider()

    # Context notes
    if state["context_notes"]:
        st.subheader("Accumulated Research Context")
        for note in state["context_notes"]:
            st.markdown(f"- {note}")
        st.divider()

    # Final report
    if state["final_report_path"]:
        st.subheader("📄 Final Report")
        try:
            with open(state["final_report_path"]) as f:
                report_md = f.read()

            # Create columns for report header and download button
            col_report, col_download = st.columns([4, 1])
            with col_report:
                st.success(f"Report ready for download")
            with col_download:
                st.download_button(
                    label="📥 Download MD",
                    data=report_md,
                    file_name=f"research_report_{session_id[:8]}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            # Markdown preview option
            with st.expander("👁 Preview Markdown Source", expanded=False):
                st.markdown("**Raw markdown code that will be downloaded:**")
                st.code(report_md, language="markdown", line_numbers=True)
                st.caption("💡 Copy this code or download the file above")

            # Display rendered report
            st.markdown(report_md)
        except Exception:
            st.warning("Could not load report file. Check the server file system.")

    # Execution controls
    if state["is_active"]:
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("Execute Next Step", type="primary"):
                with st.spinner("Executing..."):
                    try:
                        exec_resp = httpx.post(
                            f"{API_URL}/agent/{session_id}/execute",
                            timeout=120,
                        )
                        if exec_resp.status_code == 200:
                            result = exec_resp.json()
                            if result["is_done"]:
                                st.success("All tasks complete!")
                            else:
                                st.success(f"Completed: {result['message']}")
                            st.rerun()
                        else:
                            st.error(f"Execution error: {exec_resp.status_code} - {exec_resp.text}")
                    except Exception as e:
                        st.error(f"Execution failed: {e}")

        with col_b:
            # Auto-run toggle
            auto_run = st.checkbox("Auto-run all remaining steps", value=False)
            if auto_run and state["is_active"]:
                st.info("Auto-running... Refresh will stop it.")
                time.sleep(1)
                try:
                    exec_resp = httpx.post(
                        f"{API_URL}/agent/{session_id}/execute",
                        timeout=120,
                    )
                    if exec_resp.status_code == 200:
                        st.rerun()
                except Exception as e:
                    st.error(f"Auto-run failed: {e}")

    # Delete session
    st.divider()
    if st.button("Delete This Session", type="secondary"):
        try:
            del_resp = httpx.delete(f"{API_URL}/agent/{session_id}", timeout=10)
            if del_resp.status_code == 204:
                st.session_state.pop("session_id", None)
                st.success("Session deleted.")
                st.rerun()
            else:
                st.error(f"Delete failed: {del_resp.status_code}")
        except Exception as e:
            st.error(f"Delete error: {e}")
