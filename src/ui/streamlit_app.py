import os
import streamlit as st
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Import Nordic theme
import sys
sys.path.append(str(Path(__file__).parent))
from theme import STREAMLIT_CSS, COLORS

st.set_page_config(
    page_title="GPTBuddyAI",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Nordic theme CSS
st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)

# Logo and header
col1, col2 = st.columns([1, 10])
with col1:
    logo_path = Path(__file__).parent / "assets" / "logo.svg"
    if logo_path.exists():
        st.image(str(logo_path), width=56)
with col2:
    st.title("GPTBuddyAI")
    st.caption("🔒 Privacy-Preserving RAG Analytics | Local-First AI")

# Sidebar configuration
st.sidebar.title("⚙️ Settings")
persist_dir = "artifacts/index"
collection = "studykit"
topk = st.sidebar.slider("Top-k passages", 3, 12, 6, 1)
max_tokens = st.sidebar.slider("Max tokens", 200, 1600, int(os.getenv("LM_MAX_TOKENS", "400")), 50)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Corpus")
st.sidebar.info("**OpenAI Conversations** + **NIST SP 800** standards")

st.markdown("### 💬 Ask a Question")
st.markdown("Query across your conversations and compliance documents with AI-powered semantic search.")

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
    with st.spinner("🔍 Searching knowledge base..."):
        answer, metas = rag_answer(question, k=topk, max_tokens=max_tokens)

    st.markdown("---")
    st.markdown("### ✨ Answer")
    st.markdown(answer)

    st.markdown("---")
    with st.expander("📚 **Citations & Sources**", expanded=True):
        for i, m in enumerate(metas, start=1):
            source_name = m.get('source', 'Unknown')
            page_num = m.get('page')
            page_str = f"page {page_num}" if page_num else "no page"

            # Style based on source type
            if 'NIST' in str(source_name):
                icon = "📄"
                label = "NIST Document"
            else:
                icon = "💬"
                label = "Conversation"

            st.markdown(f"{icon} **[{i}]** {source_name} ({page_str})")
else:
    # Welcome message when no query yet
    st.markdown("---")
    st.info("👋 **Welcome!** Ask any question about your conversations or NIST compliance standards. The AI will search across your entire knowledge base and provide cited answers.")
