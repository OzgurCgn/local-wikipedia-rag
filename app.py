import streamlit as st
from rag_core import generate_answer

st.set_page_config(page_title="Local Wiki RAG", page_icon="📚")

st.title("📚 Local Wikipedia RAG Assistant")
st.markdown("Ask questions about famous people and places. Powered by local LLMs.")

with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
    st.markdown("---")
    st.markdown("**Note:** Make sure you have run `python ingest.py` in your terminal first to populate the local database.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("E.g., What did Marie Curie discover?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching local database and thinking..."):
            answer, sources = generate_answer(prompt)
            st.markdown(answer)
            
            if sources:
                with st.expander("🔍 View Retrieved Context"):
                    for i, src in enumerate(sources):
                        st.write(f"**Source {i+1}:** {src}")
            
    st.session_state.messages.append({"role": "assistant", "content": answer})