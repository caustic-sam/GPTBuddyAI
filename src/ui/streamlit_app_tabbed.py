import os
import streamlit as st
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

# Import Nordic theme
sys.path.append(str(Path(__file__).parent))
from theme import STREAMLIT_CSS, COLORS

# Import topic browser component
sys.path.append(str(Path(__file__).parent / "components"))
from topic_browser import render_topic_browser

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

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Knowledge Base")
st.sidebar.info("**55K+ conversations** + **NIST SP 800** standards")

# Tab navigation
tab1, tab2, tab3 = st.tabs(["💬 My Conversations", "🔍 RAG Query", "📄 NIST Library"])

# ============================================================================
# TAB 1: MY CONVERSATIONS (Topic Browser)
# ============================================================================
with tab1:
    render_topic_browser()

# ============================================================================
# TAB 2: RAG QUERY (Original functionality)
# ============================================================================
with tab2:
    st.markdown("## 🔍 Ask Questions")
    st.markdown("Query across your conversations and compliance documents with AI-powered semantic search.")

    # Settings in expander
    with st.expander("⚙️ Query Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            topk = st.slider("Top-k passages", 3, 12, 6, 1)
        with col2:
            max_tokens = st.slider("Max tokens", 200, 1600, int(os.getenv("LM_MAX_TOKENS", "400")), 50)

    st.markdown("---")

    question = st.text_input("Ask a question:", placeholder="e.g., What is the current guidance around establishing digital identity?")
    ask = st.button("Answer", type="primary")

    # Initialize RAG components
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
                if 'NIST' in str(source_name).upper() or '.pdf' in str(source_name).lower():
                    icon = "📄"
                    label = "NIST Document"
                else:
                    icon = "💬"
                    label = "Conversation"

                st.markdown(f"{icon} **[{i}]** {source_name} ({page_str})")
    else:
        # Sample queries
        st.markdown("---")
        st.info("👋 **Try these sample queries:**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🧠 Personal Insights:**
            - What are my main AI topics?
            - Summarize my thoughts on privacy
            - What did I explore in 2024?
            """)
        with col2:
            st.markdown("""
            **📄 NIST Reference:**
            - What is AC-2 access control?
            - Digital identity guidance
            - MFA requirements in SP 800-53
            """)

# ============================================================================
# TAB 3: NIST LIBRARY
# ============================================================================
with tab3:
    st.markdown("## 📄 NIST Knowledge Base")
    st.markdown("Compliance reference library powered by NIST Special Publications")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Documents Indexed", "13", help="NIST SP 800 series documents")

    with col2:
        st.metric("Total Pages", "1,544", help="Searchable pages")

    with col3:
        st.metric("Expansion Ready", "200+", help="Additional docs available")

    st.markdown("---")

    st.markdown("### 📚 Current Library")

    st.markdown("""
    **Indexed Documents:**
    - ✅ NIST SP 800-53r5 - Security & Privacy Controls
    - ✅ NIST SP 800-63-4 - Digital Identity Guidelines
    - ✅ NIST SP 800-37r2 - Risk Management Framework
    - ✅ And 10 more...

    **📂 Ready to Add More Documents?**

    Drop your NIST PDFs into `/data/nist/` and run:
    """)

    st.code("""
# Bulk ingest new documents
python src/ingest/ingest_nist_bulk.py --input data/nist --output artifacts/docs.parquet

# Rebuild index
python src/rag/build_index.py --inputs artifacts/openai.parquet artifacts/docs.parquet --persist artifacts/index --name studykit
    """, language="bash")

    st.markdown("---")

    st.markdown("### 🔍 Quick Reference")

    # Control family navigator (placeholder)
    control_family = st.selectbox(
        "Select Control Family",
        ["All", "AC - Access Control", "IA - Identification & Authentication",
         "SC - System & Communications Protection", "AU - Audit & Accountability"]
    )

    if control_family != "All":
        st.info(f"💡 Filter RAG queries to show only {control_family} controls")
        st.markdown("*Feature coming soon: Click to see all controls in this family*")
