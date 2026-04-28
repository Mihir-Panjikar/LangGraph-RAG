"""
LangGraph RAG Assistant — Streamlit Frontend

Single-page interactive Q&A interface with document management and feedback.
"""
import streamlit as st
import uuid
from api import (
    query_backend_stream,
    ingest_document,
    get_documents,
    submit_feedback,
    check_backend_health,
)

# ── Page configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="LangGraph RAG Frontend",
    page_icon="🤖",
    layout="wide",
)

# ── Custom CSS for polish ────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Subtle separator between tabs and content */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    /* Feedback buttons inline */
    div[data-testid="stHorizontalBlock"] > div {
        padding: 0 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 LangGraph RAG Assistant")

# ── Backend connectivity indicator ──────────────────────────────────
backend_online = check_backend_health()
if backend_online:
    st.caption("🟢 Backend connected")
else:
    st.warning("🔴 Backend unreachable — start the FastAPI server on port 8000")

# ── Session state defaults ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []  # list[dict] with role, content, query_id

# ── Tabs ────────────────────────────────────────────────────────────
chat_tab, ingest_tab, docs_tab = st.tabs(
    ["💬 Chat", "📤 Ingest Document", "📂 View Documents"]
)

# ═══════════════════════════════════════════════════════════════════
#  Chat Tab
# ═══════════════════════════════════════════════════════════════════
with chat_tab:
    # Render conversation history with feedback buttons
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Feedback buttons for assistant messages
            if msg["role"] == "assistant":
                query_id = msg.get("query_id", "")
                fb_key = f"fb_{i}"
                already_rated = msg.get("feedback_sent", False)

                if already_rated:
                    st.caption("✅ Feedback submitted — thank you!")
                else:
                    col1, col2, col3 = st.columns([0.06, 0.06, 0.88])
                    with col1:
                        if st.button("👍", key=f"up_{i}", help="Helpful"):
                            try:
                                submit_feedback(query_id, rating=1)
                                st.session_state.messages[i]["feedback_sent"] = True
                                st.rerun()
                            except Exception as e:
                                st.error(f"Feedback failed: {e}")
                    with col2:
                        if st.button("👎", key=f"down_{i}", help="Not helpful"):
                            try:
                                submit_feedback(query_id, rating=0)
                                st.session_state.messages[i]["feedback_sent"] = True
                                st.rerun()
                            except Exception as e:
                                st.error(f"Feedback failed: {e}")

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents…"):
        # Show user message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and stream assistant response
        query_id = str(uuid.uuid4())
        with st.chat_message("assistant"):
            try:
                full_response = st.write_stream(query_backend_stream(prompt))
            except Exception as e:
                full_response = f"⚠️ Error communicating with backend: {e}"
                st.error(full_response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "query_id": query_id,
                "feedback_sent": False,
            }
        )
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
#  Ingest Document Tab
# ═══════════════════════════════════════════════════════════════════
with ingest_tab:
    uploaded_file = st.file_uploader(
        "Upload a document to ingest into the knowledge base",
        type=["pdf", "docx", "txt", "md"],
    )
    if uploaded_file and st.button("🚀 Ingest", type="primary"):
        with st.spinner(f"Ingesting **{uploaded_file.name}** …"):
            try:
                result = ingest_document(uploaded_file.name, uploaded_file.read())
                st.success(f"✅ {result.get('message', uploaded_file.name)}")
            except Exception as e:
                st.error(f"❌ Ingestion failed: {e}")

# ═══════════════════════════════════════════════════════════════════
#  View Documents Tab
# ═══════════════════════════════════════════════════════════════════
with docs_tab:
    col_refresh, _ = st.columns([0.15, 0.85])
    with col_refresh:
        refresh_clicked = st.button("🔄 Refresh")

    # Auto-load on first visit or manual refresh
    if refresh_clicked or "docs_loaded" not in st.session_state:
        try:
            docs = get_documents()
            st.session_state.docs_cache = docs
            st.session_state.docs_loaded = True
        except Exception as e:
            st.error(f"❌ Could not fetch documents: {e}")
            st.session_state.docs_cache = []
            st.session_state.docs_loaded = True

    docs = st.session_state.get("docs_cache", [])
    if docs:
        st.dataframe(
            docs,
            use_container_width=True,
            column_config={
                "filename": st.column_config.TextColumn("Filename"),
                "chunk_count": st.column_config.NumberColumn("Chunks"),
                "timestamp": st.column_config.TextColumn("Ingested At"),
            },
        )
    elif st.session_state.get("docs_loaded"):
        st.info("No documents ingested yet. Upload one in the **Ingest Document** tab.")