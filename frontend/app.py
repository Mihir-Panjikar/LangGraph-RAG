import streamlit as st
import asyncio
from api import query_backend_stream, ingest_document, get_documents, submit_feedback

st.set_page_config(page_title="LangGraph RAG Frontend", layout="wide")

st.title("🤖 LangGraph RAG Assistant")

if 'messages' not in st.session_state:
    st.session_state.messages = []

chat_tab, ingest_tab, docs_tab = st.tabs(["💬 Chat", "📤 Ingest Document", "📂 View Documents"])

with chat_tab:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
    if p := st.chat_input('Ask...'):
        st.session_state.messages.append({'role': 'user', 'content': p})
        with st.chat_message('user'): st.markdown(p)
        with st.chat_message('assistant'):
            ph = st.empty()
            res_container = {'text': ''}
            try:
                async def stream_response():
                    async for chunk in query_backend_stream(p):
                        res_container['text'] += chunk
                        ph.markdown(res_container['text'] + '▌')
                    ph.markdown(res_container['text'])
                asyncio.run(stream_response())
                st.session_state.messages.append({'role': 'assistant', 'content': res_container['text']})
                st.rerun()
            except Exception as e: ph.error(str(e))

with ingest_tab:
    f = st.file_uploader('Upload', type=['pdf', 'docx', 'txt', 'md'])
    if f and st.button('Ingest'):
        with st.spinner('...'):
            try:
                r = asyncio.run(ingest_document(f.name, f.read()))
                st.success(f.name)
            except Exception as e: st.error(str(e))

with docs_tab:
    if st.button('Refresh'):
        try:
            d = asyncio.run(get_documents())
            st.table(d)
        except Exception as e: st.error(str(e))