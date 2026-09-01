import os
import markdown as md_lib
import requests
import streamlit as st
from typing import Optional, Dict, Any, List, Tuple
from streamlit_local_storage import LocalStorage

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="Agentic Communication Helper",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #0d0d0d !important;
        color: #ececec !important;
    }
    
    /* ── Main Container & Layout ── */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 1rem !important;
    }
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 6.5rem !important;
        max-width: 800px !important;
    }
    
    /* ── Sidebar (ChatGPT style) ── */
    section[data-testid="stSidebar"] {
        background-color: #171717 !important;
        border-right: 1px solid #212121 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 0.4rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ececec !important;
    }
    .sidebar-header-box {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
        padding: 0 0.2rem 0.55rem 0.2rem;
        margin-top: -0.15rem !important;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #212121;
    }
    .sidebar-brand-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .sidebar-brand-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #ffffff !important;
        letter-spacing: -0.01em;
    }
    .sidebar-brand-badge {
        font-size: 0.65rem;
        background: #262626;
        color: #a3a3a3 !important;
        padding: 0.15rem 0.45rem;
        border-radius: 0.35rem;
        font-weight: 500;
    }
    .sidebar-status-row {
        font-size: 0.7rem;
        color: #737373 !important;
        font-weight: 400;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        margin-top: 0.1rem;
    }
    section[data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 0.84rem !important;
        font-weight: 400 !important;
        padding: 0.45rem 0.6rem !important;
        border-radius: 0.5rem !important;
        width: 100% !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        color: #b4b4b4 !important;
        transition: background 0.12s, color 0.12s !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #212121 !important;
        color: #ffffff !important;
    }
    .active-chat button {
        background-color: #212121 !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .new-chat-btn button {
        border: 1px solid #2e2e2e !important;
        border-radius: 0.55rem !important;
        font-weight: 500 !important;
        color: #ececec !important;
        padding: 0.45rem 0.75rem !important;
        margin-bottom: 0.5rem !important;
    }
    .new-chat-btn button:hover {
        background-color: #212121 !important;
        border-color: #3e3e3e !important;
    }
    .sidebar-section-label {
        color: #8e8ea0 !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        padding: 0.9rem 0.5rem 0.65rem !important;
        margin-bottom: 0.35rem !important;
        display: block !important;
        position: relative !important;
        z-index: 2 !important;
        pointer-events: none !important;
    }
    
    /* Clean sidebar container gaps */
    section[data-testid="stSidebar"] .stButton { margin: 1px 0 !important; padding: 0 !important; }
    section[data-testid="stSidebar"] [data-testid="element-container"],
    section[data-testid="stSidebar"] .element-container { margin: 0 !important; padding: 0 !important; background: transparent !important; }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div { gap: 1px !important; margin: 0 !important; background: transparent !important; }
    
    /* ── Main Chat Area ── */
    [data-testid="stChatMessage"] { display: none !important; }
    .chat-area {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        padding: 0.5rem 0 1rem;
    }
    
    /* User message: clean right-aligned pill bubble (ChatGPT style) */
    .user-msg-row {
        display: flex;
        justify-content: flex-end;
        width: 100%;
        margin-bottom: 0.25rem;
    }
    .user-bubble {
        background-color: #212121;
        color: #ececec;
        padding: 0.65rem 1rem;
        border-radius: 1.25rem;
        max-width: 75%;
        font-size: 0.92rem;
        line-height: 1.55;
        word-break: break-word;
    }
    
    /* Assistant message: frameless, left-aligned, native markdown on page (ChatGPT style) */
    .assistant-msg-row {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        width: 100%;
        margin-bottom: 0.75rem;
    }
    .intent-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background-color: rgba(59, 130, 246, 0.1);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 9999px;
        padding: 0.15rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .assistant-content {
        color: #ececec;
        font-size: 0.93rem;
        line-height: 1.7;
        width: 100%;
    }
    .assistant-content p { margin: 0 0 0.75rem 0; }
    .assistant-content p:last-child { margin-bottom: 0; }
    .assistant-content strong { color: #ffffff; font-weight: 600; }
    .assistant-content em { font-style: italic; color: #d4d4d8; }
    .assistant-content ul, .assistant-content ol { margin: 0.4rem 0 0.8rem 1.4rem; padding: 0; }
    .assistant-content li { margin-bottom: 0.3rem; }
    .assistant-content code { background: rgba(255,255,255,0.08); color: #f472b6; padding: 0.15rem 0.35rem; border-radius: 0.25rem; font-size: 0.84rem; font-family: monospace; }
    .assistant-content pre { background: #171717; border: 1px solid #262626; padding: 0.75rem 1rem; border-radius: 0.5rem; overflow-x: auto; margin: 0.6rem 0; }
    .assistant-content pre code { background: transparent; color: #e4e4e7; padding: 0; }
    
    .clarification-box {
        background-color: rgba(245, 158, 11, 0.08);
        border-left: 3px solid #f59e0b;
        padding: 0.6rem 0.85rem;
        border-radius: 0 0.5rem 0.5rem 0;
        margin: 0.4rem 0;
    }
    .clarification-title { color: #fbbf24; font-weight: 600; font-size: 0.8rem; margin-bottom: 0.25rem; }
    
    /* ── Tabs (minimalistic) ── */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; border-bottom: 1px solid #212121; margin-bottom: 1rem; }
    .stTabs [data-baseweb="tab"] { font-size: 0.86rem; font-weight: 500; color: #737373; padding: 0.4rem 0.8rem; background: transparent !important; }
    .stTabs [aria-selected="true"] { color: #ffffff !important; border-bottom: 2px solid #ffffff !important; }
    
    /* ── ChatGPT Bottom Input Bar ── */
    [data-testid="stBottom"] {
        background: transparent !important;
        border: none !important;
        padding: 0.6rem 0 1.2rem !important;
    }
    [data-testid="stBottom"] > div {
        max-width: 800px !important;
        margin: 0 auto !important;
        padding: 0 1rem !important;
    }
    [data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"] > div {
        background-color: #212121 !important;
        border: 1px solid #303030 !important;
        border-radius: 1.75rem !important;
        box-shadow: none !important;
        padding: 0.2rem 0.6rem !important;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #4a4a4a !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ececec !important;
        font-size: 0.9rem !important;
        background: transparent !important;
        caret-color: #ffffff !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #737373 !important;
    }
    
    .result-box {
        background: #171717;
        border: 1px solid #262626;
        border-radius: 0.65rem;
        padding: 1.1rem 1.3rem;
        line-height: 1.65;
        font-size: 0.9rem;
        color: #d4d4d8;
    }
    .result-box p { margin: 0 0 0.6rem 0; }
    .result-box p:last-child { margin-bottom: 0; }
    .result-box strong { color: #ffffff; font-weight: 600; }
    .result-box em { font-style: italic; color: #a1a1aa; }
    .result-box ul, .result-box ol { margin: 0.4rem 0 0.6rem 1.3rem; padding: 0; }
    .result-box li { margin-bottom: 0.25rem; }
    .result-box code { background: rgba(255,255,255,0.08); color: #f472b6; padding: 0.15rem 0.35rem; border-radius: 0.25rem; font-size: 0.84rem; font-family: monospace; }
    </style>
    """,
    unsafe_allow_html=True,
)

localS = LocalStorage()
LOCAL_STORAGE_KEY = "coach_conversation_index"
LOCAL_SESSION_KEY = "coach_current_session"


def check_backend_health() -> bool:
    try:
        res = requests.get(f"{BACKEND_URL}/", timeout=3)
        return res.status_code == 200
    except Exception:
        return False


def call_chat_endpoint(message: str, session_id) -> tuple:
    payload: Dict[str, Any] = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    try:
        response = requests.post(f"{BACKEND_URL}/coach/chat", json=payload, timeout=90)
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 400:
            return None, f"Invalid input: {response.json().get('detail', 'Message cannot be empty.')}"
        elif response.status_code == 503:
            return None, "The assistant is busy right now, please try again in a moment."
        return None, f"Backend returned status {response.status_code}. Please try again."
    except requests.exceptions.Timeout:
        return None, "The request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return None, f"Could not connect to backend at {BACKEND_URL}."
    except Exception:
        return None, "An unexpected error occurred. Please try again."


def call_analyze_endpoint(text: str) -> tuple:
    try:
        response = requests.post(f"{BACKEND_URL}/coach/analyze", json={"text": text}, timeout=90)
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 400:
            return None, f"Invalid input: {response.json().get('detail', 'Text cannot be empty.')}"
        elif response.status_code == 503:
            return None, "The assistant is busy right now, please try again in a moment."
        return None, f"Analysis failed with status {response.status_code}."
    except requests.exceptions.Timeout:
        return None, "Analysis timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return None, f"Could not connect to backend at {BACKEND_URL}."
    except Exception:
        return None, "The assistant is busy right now, please try again."


def call_improve_endpoint(text: str, improvement_type: str) -> tuple:
    payload = {"text": text, "improvement_type": improvement_type}
    try:
        response = requests.post(f"{BACKEND_URL}/coach/improve", json=payload, timeout=90)
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 400:
            return None, f"Invalid input: {response.json().get('detail', 'Text cannot be empty.')}"
        elif response.status_code == 503:
            return None, "The assistant is busy right now, please try again in a moment."
        return None, f"Improvement failed with status {response.status_code}."
    except requests.exceptions.Timeout:
        return None, "Improvement request timed out."
    except requests.exceptions.ConnectionError:
        return None, f"Could not connect to backend at {BACKEND_URL}."
    except Exception:
        return None, "The assistant is busy right now, please try again."


def call_history_endpoint(session_id: str) -> tuple:
    try:
        response = requests.get(f"{BACKEND_URL}/coach/history/{session_id.strip()}", timeout=30)
        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 404:
            return None, "No history found for this session ID."
        return None, f"Failed to fetch history (Status: {response.status_code})."
    except requests.exceptions.ConnectionError:
        return None, f"Could not connect to backend at {BACKEND_URL}."
    except Exception:
        return None, "Failed to load session history."


def make_title(first_message: str) -> str:
    text = first_message.strip().replace("\n", " ")
    return (text[:40] + "...") if len(text) > 40 else text


def load_index_from_local_storage() -> dict:
    try:
        raw = localS.getItem(LOCAL_STORAGE_KEY)
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, str):
            import json
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
    except Exception:
        pass
    return {}


def save_index_to_local_storage(index: dict):
    try:
        localS.setItem(LOCAL_STORAGE_KEY, index, key="set_conv_index")
    except Exception:
        pass


if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_index" not in st.session_state:
    st.session_state.conversation_index = {}
if "index_hydrated" not in st.session_state:
    st.session_state.index_hydrated = False
if "is_new_chat" not in st.session_state:
    st.session_state.is_new_chat = False
if "pending_storage_save" not in st.session_state:
    st.session_state.pending_storage_save = False

# Render pending localStorage save if flagged (runs as part of normal page render)
if st.session_state.pending_storage_save:
    save_index_to_local_storage(st.session_state.conversation_index)
    if st.session_state.session_id:
        try:
            localS.setItem(LOCAL_SESSION_KEY, st.session_state.session_id, key="set_cur_sess")
        except Exception:
            pass
    st.session_state.pending_storage_save = False

if not st.session_state.index_hydrated:
    stored_index = load_index_from_local_storage()
    if stored_index:
        st.session_state.conversation_index = stored_index
        st.session_state.index_hydrated = True


def sync_session_to_url(session_id):
    if session_id:
        st.query_params["session"] = session_id
    elif "session" in st.query_params:
        del st.query_params["session"]


def restore_active_session():
    """Restore conversation messages from Firestore on refresh."""
    if st.session_state.is_new_chat:
        return
    if st.session_state.session_id is not None and st.session_state.messages:
        return

    url_session_id = st.query_params.get("session")
    if url_session_id:
        if isinstance(url_session_id, list):
            url_session_id = url_session_id[0]
        url_session_id = str(url_session_id).strip()

    target_session_id = url_session_id
    if not target_session_id:
        try:
            saved_sess = localS.getItem(LOCAL_SESSION_KEY)
            if saved_sess and isinstance(saved_sess, str):
                target_session_id = saved_sess
        except Exception:
            pass

    if not target_session_id and st.session_state.conversation_index:
        target_session_id = list(st.session_state.conversation_index.keys())[-1]

    if target_session_id:
        history_turns, err = call_history_endpoint(target_session_id)
        if not err and history_turns:
            st.session_state.session_id = target_session_id
            st.session_state.messages = [
                {"role": t["role"], "content": t["content"], "intent": t.get("intent"), "clarify_pending": False}
                for t in history_turns
            ]
            sync_session_to_url(target_session_id)


restore_active_session()


def register_conversation(session_id: str, first_user_message: str):
    st.session_state.is_new_chat = False
    if session_id not in st.session_state.conversation_index:
        st.session_state.conversation_index[session_id] = make_title(first_user_message)
    st.session_state.pending_storage_save = True


def start_new_conversation():
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.is_new_chat = True
    sync_session_to_url(None)
    try:
        localS.deleteItem(LOCAL_SESSION_KEY, key="del_cur_sess")
    except Exception:
        pass


def open_conversation(session_id: str):
    st.session_state.is_new_chat = False
    history_turns, err = call_history_endpoint(session_id)
    if not err and history_turns is not None:
        st.session_state.session_id = session_id
        st.session_state.messages = [
            {"role": t["role"], "content": t["content"], "intent": t.get("intent"), "clarify_pending": False}
            for t in history_turns
        ]
        sync_session_to_url(session_id)
        st.session_state.pending_storage_save = True
    return err


def md_to_html(text: str) -> str:
    """Convert markdown text to HTML for safe injection into custom bubbles."""
    return md_lib.markdown(
        text,
        extensions=["nl2br", "sane_lists"],
    )


def render_message(msg: dict):
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        # User message: clean right-aligned pill bubble (ChatGPT style)
        st.markdown(
            f"<div class='user-msg-row'>"
            f"<div class='user-bubble'>{content}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        # Assistant message: frameless, left-aligned, native typography on page (ChatGPT style)
        intent = msg.get("intent")
        clarify = msg.get("clarify_pending", False)
        badge = f"<div class='intent-badge'>🎯 {intent}</div>" if intent else ""
        html_content = md_to_html(content)
        if clarify:
            body = (
                f"{badge}<div class='clarification-box'>"
                f"<div class='clarification-title'>❓ Clarification Needed</div>"
                f"<div class='assistant-content'>{html_content}</div></div>"
            )
        else:
            body = f"{badge}<div class='assistant-content'>{html_content}</div>"
        st.markdown(
            f"<div class='assistant-msg-row'>{body}</div>",
            unsafe_allow_html=True,
        )


# --- Sidebar ---

with st.sidebar:
    is_healthy = check_backend_health()
    status_text = "🟢 Connected" if is_healthy else "🔴 Offline"
    
    st.markdown(
        f"""
        <div class='sidebar-header-box'>
            <div class='sidebar-brand-row'>
                <span class='sidebar-brand-title'>CMHelper</span>
                <span class='sidebar-brand-badge'>AI Coach</span>
            </div>
            <div class='sidebar-status-row'>
                <span>{status_text}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("<div class='new-chat-btn'>", unsafe_allow_html=True)
    if st.button("＋  New chat", use_container_width=True):
        start_new_conversation()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-label'>Chats</div>", unsafe_allow_html=True)
    if not st.session_state.conversation_index:
        st.caption("No previous chats yet.")
    else:
        for sid, title in reversed(list(st.session_state.conversation_index.items())):
            is_active = sid == st.session_state.session_id
            wrapper_class = "active-chat" if is_active else ""
            st.markdown(f"<div class='{wrapper_class}'>", unsafe_allow_html=True)
            if st.button(title or "Untitled chat", key=f"open_{sid}", use_container_width=True):
                err = open_conversation(sid)
                if err:
                    st.error(err)
                else:
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("🔍 Load session by ID"):
        paste_session_id = st.text_input("Session ID:", label_visibility="collapsed", placeholder="e.g. 123e4567-e89b...")
        if st.button("Load", use_container_width=True):
            if paste_session_id.strip():
                with st.spinner("Fetching..."):
                    err = open_conversation(paste_session_id.strip())
                    if err:
                        st.error(err)
                    else:
                        register_conversation(
                            paste_session_id.strip(),
                            st.session_state.messages[0]["content"] if st.session_state.messages else "Untitled chat",
                        )
                        st.rerun()
            else:
                st.warning("Enter a session ID.")


# --- Main area ---

tab_chat, tab_analyze, tab_improve = st.tabs(["💬 Chat", "📊 Analyze", "✨ Improve"])

with tab_chat:
    st.markdown("<div class='chat-area'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        render_message(msg)
    st.markdown("</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Ask anything...")

    if user_input and user_input.strip():
        cleaned_input = user_input.strip()
        is_first_message = len(st.session_state.messages) == 0
        st.session_state.messages.append({"role": "user", "content": cleaned_input})
        with st.spinner("Thinking..."):
            res, err = call_chat_endpoint(cleaned_input, st.session_state.session_id)
        if err:
            st.error(err)
        elif res:
            response_text = res.get("response", "")
            detected_intent = res.get("intent", "unclear")
            session_id = res.get("session_id")
            clarify_pending = res.get("clarify_pending", False)
            if session_id:
                st.session_state.session_id = session_id
                sync_session_to_url(session_id)
                register_conversation(session_id, cleaned_input)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "intent": detected_intent,
                "clarify_pending": clarify_pending,
            })
        st.rerun()

with tab_analyze:
    st.subheader("Message Analysis")
    analyze_input = st.text_area("Paste text to evaluate:", height=160, key="analyze_text_input")
    if st.button("Analyze", type="primary"):
        if not analyze_input.strip():
            st.error("Please enter some text to analyze.")
        else:
            with st.spinner("Analyzing..."):
                res, err = call_analyze_endpoint(analyze_input.strip())
            if err:
                st.error(err)
            elif res:
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Clarity", f"{res.get('clarity', 0)}/5")
                m2.metric("Tone", f"{res.get('tone', 0)}/5")
                m3.metric("Grammar", f"{res.get('grammar', 0)}/5")
                m4.metric("Conciseness", f"{res.get('conciseness', 0)}/5")
                
                reasoning = res.get("reasoning", "")
                feedback = res.get("feedback", "")
                if reasoning:
                    st.markdown(f"<div class='result-box' style='margin-bottom:0.75rem;'><strong>Reasoning:</strong><br>{md_to_html(reasoning)}</div>", unsafe_allow_html=True)
                if feedback:
                    st.markdown(f"<div class='result-box'><strong>Feedback:</strong><br>{md_to_html(feedback)}</div>", unsafe_allow_html=True)

with tab_improve:
    st.subheader("Improve a Draft")
    improve_input = st.text_area("Text to improve:", height=160, key="improve_text_input")
    choice = st.radio("Focus:", ["Grammar", "Tone", "Conversation"], horizontal=True)
    type_map = {"Grammar": "grammar", "Tone": "tone", "Conversation": "conversation"}
    if st.button("Improve", type="primary"):
        if not improve_input.strip():
            st.error("Please enter some text to improve.")
        else:
            with st.spinner("Improving..."):
                res, err = call_improve_endpoint(improve_input.strip(), type_map[choice])
            if err:
                st.error(err)
            elif res:
                result_text = res.get("result", "")
                html_output = md_to_html(result_text)
                st.markdown(f"<div class='result-box'>{html_output}</div>", unsafe_allow_html=True)
