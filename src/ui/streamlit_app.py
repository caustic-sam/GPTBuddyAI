import os
import streamlit as st
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="GPTBuddyAI RAG", layout="wide")

persist_dir = "artifacts/index"
collection = "studykit"
topk = st.sidebar.slider("Top-k passages", 3, 12, 6, 1)
max_tokens = st.sidebar.slider("Max tokens", 200, 1600, int(os.getenv("LM_MAX_TOKENS", "400")), 50)

st.title("GPTBuddyAI — Multi-Corpus RAG")
st.caption("OpenAI Chats + NIST SP 800 + IAPP (local, private)")

question = st.text_input("Ask a question:", placeholder="e.g., Summarize AC-2 in NIST 800-53r5")
ask = st.button("Answer")

if "embed" not in st.session_state:
    st.session_state["embed"] = SentenceTransformer("all-MiniLM-L6-v2")
if "client" not in st.session_state:
    st.session_state["client"] = PersistentClient(path=persist_dir)
if "coll" not in st.session_state:
    st.session_state["coll"] = st.session_state["client"].get_collection(collection)

def rag_answer(q, k=6, max_tokens=400):
    embed = st.session_state["embed"]
    coll = st.session_state["coll"]
    qv = embed.encode([q])[0].tolist()
    r = coll.query(query_embeddings=[qv], n_results=k)
    chunks = r["documents"][0]
    metas = r["metadatas"][0]

    context = ""
    for i, (c, m) in enumerate(zip(chunks, metas), start=1):
        cite = f"[{i}] source={m.get('source')} page={m.get('page')}"
        context += f"{cite}\n{c}\n\n"

    from mlx_lm import load, generate
    model_id = os.getenv("LM_MODEL", "mlx-community/SmolLM2-1.7B-Instruct-4bit")
    model, tok = load(model_id)
    prompt = f"Use the CONTEXT to answer with inline citations like [1], [2].\n\nCONTEXT:\n{context}\nQ: {q}\nA:"
    out = generate(model, tok, prompt, max_tokens=max_tokens)
    return out, metas

if ask and question.strip():
    with st.spinner("Thinking..."):
        answer, metas = rag_answer(question, k=topk, max_tokens=max_tokens)
    st.subheader("Answer")
    st.write(answer)
    with st.expander("Citations"):
        for i, m in enumerate(metas, start=1):
            st.write(f"[{i}] {m.get('source')} (page {m.get('page')})")
