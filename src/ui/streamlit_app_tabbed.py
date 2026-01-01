import os
import streamlit as st
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

# Import Nordic theme
sys.path.append(str(Path(__file__).parent))
from theme import STREAMLIT_CSS, COLORS

# Import UI components
sys.path.append(str(Path(__file__).parent / "components"))
from topic_browser import render_topic_browser
from agent_workflows import render_agent_workflows
from knowledge_graph import render_knowledge_graph

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
st.sidebar.info("**55K+ conversations** + **337 NIST documents** (32K pages)")
st.sidebar.metric("Searchable Chunks", "60,310")

# Tab navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 My Conversations", "🔍 RAG Query", "📄 NIST Library", "🤖 Agent Workflows", "🕸️ Knowledge Graph"])

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

    # Initialize RAG components with error handling
    # 1. Initialize embedding model
    if "embed" not in st.session_state:
        try:
            with st.spinner("🔄 Loading embedding model (all-MiniLM-L6-v2)..."):
                st.session_state["embed"] = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            st.error(f"❌ Failed to load embedding model: {str(e)[:200]}")
            st.info("💡 Check internet connection for model download or verify sentence-transformers installation")
            st.code("pip install --upgrade sentence-transformers", language="bash")
            st.session_state["embed"] = None

    # 2. Initialize ChromaDB client
    if "client" not in st.session_state:
        try:
            st.session_state["client"] = PersistentClient(path=persist_dir)
        except Exception as e:
            st.error(f"❌ Failed to connect to ChromaDB: {str(e)[:200]}")
            st.info(f"💡 Verify the index directory exists:")
            st.code(f"ls -la {persist_dir}", language="bash")
            st.session_state["client"] = None

    # 3. Get collection
    if "coll" not in st.session_state:
        client = st.session_state.get("client")
        if client:
            try:
                st.session_state["coll"] = client.get_collection(collection)
            except Exception as e:
                st.error(f"❌ Collection '{collection}' not found: {str(e)[:200]}")

                # Show available collections
                try:
                    available = [c.name for c in client.list_collections()]
                    if available:
                        st.warning(f"Available collections: {', '.join(available)}")
                    else:
                        st.warning("No collections found in the database")
                except:
                    pass

                st.info("💡 Build the index:")
                st.code("""python src/rag/build_index.py \\
  --inputs artifacts/openai.parquet artifacts/docs.parquet \\
  --persist artifacts/index \\
  --name studykit""", language="bash")
                st.session_state["coll"] = None
        else:
            st.session_state["coll"] = None

    def rag_answer(q, k=6, max_tokens=400):
        """RAG answer with comprehensive error handling"""

        # 1. VALIDATE SESSION STATE COMPONENTS
        embed = st.session_state.get("embed")
        coll = st.session_state.get("coll")

        if not embed:
            st.error("❌ Embedding model not loaded")
            st.info("💡 Refresh the page to retry loading the model")
            return None, []

        if not coll:
            st.error("❌ Knowledge base not connected")
            st.info("💡 Build the index:")
            st.code("""python src/rag/build_index.py \\
  --inputs artifacts/openai.parquet artifacts/docs.parquet \\
  --persist artifacts/index \\
  --name studykit""", language="bash")
            return None, []

        # 2. ENCODE QUERY
        try:
            qv = embed.encode([q])[0].tolist()
        except Exception as e:
            st.error(f"❌ Failed to encode query: {str(e)[:200]}")
            st.info("💡 Try rephrasing your question or shortening very long queries")
            return None, []

        # 3. QUERY CHROMADB
        try:
            r = coll.query(query_embeddings=[qv], n_results=k)

            # Validate response structure
            if not r or "documents" not in r or not r["documents"]:
                st.warning("⚠️ No relevant documents found in the knowledge base")
                st.info("💡 Try using different keywords or asking a more general question")
                return None, []

            chunks = r["documents"][0]
            metas = r["metadatas"][0]

            if not chunks:
                st.warning("⚠️ No results returned for this query")
                return None, []

        except Exception as e:
            st.error(f"❌ Database query failed: {str(e)[:200]}")
            st.info("💡 The index may be corrupted. Try rebuilding:")
            st.code("""# Backup old index
mv artifacts/index artifacts/index.bak

# Rebuild
python src/rag/build_index.py \\
  --inputs artifacts/openai.parquet artifacts/docs.parquet \\
  --persist artifacts/index \\
  --name studykit""", language="bash")
            return None, []

        # 4. BUILD CONTEXT
        try:
            context = ""
            for i, (c, m) in enumerate(zip(chunks, metas), start=1):
                # Safely extract metadata with defaults
                source = m.get('source', 'Unknown Source')
                page = m.get('page', 'N/A')
                cite = f"[{i}] source={source} page={page}"
                context += f"{cite}\n{c}\n\n"

        except Exception as e:
            st.error(f"❌ Failed to build context from results: {str(e)[:200]}")
            st.warning("This might indicate corrupt metadata in the index")
            return None, []

        # 5. LOAD AND RUN LLM
        try:
            from mlx_lm import load, generate

            model_id = os.getenv("LM_MODEL", "mlx-community/SmolLM2-1.7B-Instruct-4bit")

            # Cache model in session state to avoid reloading
            if "llm_model" not in st.session_state or st.session_state["llm_model"] is None:
                with st.spinner(f"🔄 Loading language model: {model_id}..."):
                    st.session_state["llm_model"] = load(model_id)

            model, tok = st.session_state["llm_model"]

            # Build prompt
            prompt = f"""Use the CONTEXT to answer with inline citations like [1], [2].

CONTEXT:
{context}

Q: {q}
A:"""

            # Generate answer
            with st.spinner("💭 Generating answer..."):
                out = generate(model, tok, prompt, max_tokens=max_tokens)

            return out, metas

        except ImportError as e:
            st.error("❌ MLX library not available")
            st.info("💡 MLX is required for local model inference:")
            st.code("pip install mlx-lm", language="bash")
            st.markdown("""
            **Note**: MLX only works on Apple Silicon Macs.
            For other platforms, consider using OpenAI API or transformers + PyTorch.
            """)
            return None, []

        except Exception as e:
            st.error(f"❌ Model generation failed: {str(e)[:200]}")
            st.info(f"💡 Try reducing max_tokens (currently: {max_tokens}) or using a different model")
            return None, []

    if ask and question.strip():
        with st.spinner("🔍 Searching knowledge base..."):
            answer, metas = rag_answer(question, k=topk, max_tokens=max_tokens)

        # Only display results if we got valid output
        if answer and metas:
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
        elif answer is None:
            # Error already displayed by rag_answer function
            st.warning("⚠️ Unable to generate an answer. Please check the errors above and try again.")
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
        st.metric("Documents Indexed", "337", delta="+324", help="NIST SP 800 series + practice guides")

    with col2:
        st.metric("Total Pages", "32,112", delta="+30,568", help="Searchable pages with full text")

    with col3:
        st.metric("Index Chunks", "60,310", delta="+32,513", help="Vector embeddings for semantic search")

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

# ============================================================================
# TAB 4: AGENT WORKFLOWS
# ============================================================================
with tab4:
    render_agent_workflows()

# ============================================================================
# TAB 5: KNOWLEDGE GRAPH
# ============================================================================
with tab5:
    render_knowledge_graph()
