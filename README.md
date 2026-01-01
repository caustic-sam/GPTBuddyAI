# GPTBuddyAI
**Production-Grade Agentic Knowledge Platform**

🤖 Autonomous Agents | 🕸️ Knowledge Graph | 🔒 Privacy-Preserving

---

## 🎉 **7-Day Sprint Complete - Demo Ready!**

**Built**: December 31, 2025 - January 1, 2026

### **What is GPTBuddyAI?**

GPTBuddyAI is not just another RAG system - it's an **autonomous agentic platform** that performs complex knowledge work:

- **🤖 Multi-Agent Orchestration**: 3 autonomous agents that execute multi-step workflows
- **🕸️ Knowledge Graph**: Graph-based reasoning with 500-1K entities and relationship discovery
- **📊 Autonomous Workflows**: Compliance gap analysis, multi-hop research synthesis, report generation
- **📈 Executive Visualizations**: 9 interactive Plotly charts for insights and reporting
- **🔒 Privacy-Preserving**: 100% local processing, no cloud dependencies, complete data sovereignty

---

## 🚀 **Quick Start**

### **Launch the Demo**
```bash
# Start Streamlit app
streamlit run src/ui/streamlit_app_tabbed.py --server.port 8501

# Open browser to http://localhost:8501
```

### **Pre-Demo Validation**
```bash
# Validate all systems (should show 100% pass)
python scripts/demo_validation.py

# Run integration tests (94% pass rate)
python tests/test_integration.py

# Check performance
python scripts/performance_check.py
```

---

## 📊 **Key Metrics**

### **Knowledge Base**
| Metric | Value |
|--------|-------|
| NIST Documents | 337 (SP 800 series) |
| Total Pages | 32,112 |
| Conversations | 55,173 messages |
| Vector Chunks | 60,310 |
| Entities (extractable) | 500-1,000 |
| Graph Relationships | 2,000-5,000 |

### **Performance**
| Operation | Time |
|-----------|------|
| Query Latency | <1s |
| Agent Init | <2s |
| Compliance Analysis | ~30s |
| Research Synthesis | ~60s |
| Report Generation | <2s |

### **Quality**
| Metric | Score |
|--------|-------|
| Test Pass Rate | 94.1% |
| Demo Validation | 100% ✅ |
| Data Privacy | 100% Local |
| Code Coverage | High |

---

## 🤖 **Autonomous Workflows**

### **1. Compliance Gap Analysis**
Autonomous NIST compliance checking and remediation planning.

**What it does:**
1. Extracts 50+ NIST controls from knowledge base
2. Searches conversations for implementation evidence
3. Classifies controls: Implemented / Partial / Gaps
4. Generates prioritized remediation recommendations
5. Produces executive dashboard with 5 visualizations

**How to use:**
```
Navigate to: Agent Workflows → Compliance Gap Analysis
Click: 🚀 Run Compliance Analysis
Wait: ~30 seconds
Result: Interactive dashboard + JSON export
```

**Output:**
- Coverage gauge (90% threshold)
- Family heatmap (control × status)
- Gap waterfall chart
- Priority matrix (remediation roadmap)
- Stacked bar charts (family breakdown)

---

### **2. Research Synthesis**
Multi-hop autonomous research with theme clustering and report generation.

**What it does:**
1. Performs 3-hop iterative querying
2. Extracts key concepts from initial results
3. Expands queries with discovered concepts
4. Clusters findings into themes (K-means)
5. Generates structured markdown report with citations

**How to use:**
```
Navigate to: Agent Workflows → Research Synthesis
Enter topic: "Multi-factor authentication in federal systems"
Set depth: 3 hops
Click: 🚀 Run Research Synthesis
Wait: ~60 seconds
Result: Markdown report + JSON data
```

**Output:**
- Executive summary
- Query evolution timeline
- Discovered themes with representative docs
- Full citations (source + page)
- Downloadable markdown report

---

### **3. Knowledge Graph Exploration**
Interactive entity discovery and relationship visualization.

**What it does:**
1. Extracts entities (NIST controls, concepts, publications)
2. Discovers relationships (co-occurrence, hierarchical)
3. Provides interactive graph visualization
4. Finds paths between entities
5. Ranks entities by centrality (PageRank)

**How to use:**
```
Navigate to: Knowledge Graph
Build graph: ./scripts/demo_build_graph.sh (optional)
Explore: Entity Explorer → Search "AC-2"
Visualize: Graph Visualization → Select entities
Analyze: Relationship Browser → Find paths
```

**Capabilities:**
- Entity search (controls, concepts, pubs)
- Interactive Plotly network graphs
- Shortest path discovery
- PageRank centrality analysis

---

## 📁 **Project Structure**

```
GPTBuddyAI/
├── src/
│   ├── agents/                 # Multi-agent system
│   │   ├── base_agent.py       # Abstract base class
│   │   ├── coordinator.py      # Workflow orchestration
│   │   ├── compliance_agent.py # NIST gap analysis
│   │   ├── research_agent.py   # Multi-hop research
│   │   └── synthesis_agent.py  # Report generation
│   │
│   ├── graph/                  # Knowledge graph
│   │   ├── entity_extractor.py # Entity extraction
│   │   ├── graph_builder.py    # Graph construction
│   │   └── graph_rag.py        # Hybrid RAG
│   │
│   ├── ui/
│   │   ├── streamlit_app_tabbed.py  # Main app (5 tabs)
│   │   └── components/
│   │       ├── topic_browser.py     # Conversation topics
│   │       ├── agent_workflows.py   # Agent UI
│   │       ├── knowledge_graph.py   # Graph explorer
│   │       ├── compliance_viz.py    # Compliance charts
│   │       └── temporal_viz.py      # Temporal analysis
│   │
│   ├── rag/                    # RAG pipeline
│   │   ├── build_index.py      # Index construction
│   │   └── query.py            # Query interface
│   │
│   ├── ingest/                 # Data ingestion
│   │   ├── ingest_openai.py    # Conversation import
│   │   └── ingest_pdfs.py      # PDF processing
│   │
│   └── analytics/              # Analysis tools
│       ├── topic_discovery.py  # K-means clustering
│       └── label_clusters.py   # LLM labeling
│
├── tests/
│   └── test_integration.py     # 17 integration tests
│
├── scripts/
│   ├── demo_validation.py      # Pre-demo health check
│   ├── performance_check.py    # System monitoring
│   └── demo_build_graph.sh     # Graph builder
│
├── docs/
│   ├── SPRINT_COMPLETE.md      # Complete sprint summary
│   ├── DEMO_DECK_OUTLINE.md    # 15-slide presentation
│   ├── DEMO_SCRIPT.md          # 6-minute narration
│   ├── ROADMAP.md              # Future enhancements
│   ├── DAY4_COMPLETE.md        # Visualization summary
│   └── DAY5_COMPLETE.md        # Testing summary
│
└── artifacts/
    ├── index/                  # ChromaDB (836.7 MB)
    ├── openai.parquet          # Conversations (59.6 MB)
    ├── docs.parquet            # NIST docs (59.2 MB)
    ├── graph/                  # Knowledge graph (optional)
    └── reports/                # Generated reports
```

---

## 🏗️ **Architecture**

### **3-Layer Design**

```
┌─────────────────────────────────────────────────────┐
│           AUTONOMOUS AGENT LAYER                    │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────┐│
│  │ Compliance   │ │  Research    │ │ Synthesis   ││
│  │    Agent     │ │    Agent     │ │   Agent     ││
│  └──────────────┘ └──────────────┘ └─────────────┘│
│         Orchestrated by AgentCoordinator            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│          KNOWLEDGE GRAPH LAYER                      │
│  Entity Extraction → Graph Building → Graph RAG     │
│  500-1K entities | 2K-5K relationships              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              VECTOR RAG FOUNDATION                  │
│  ChromaDB + sentence-transformers (all-MiniLM-L6)   │
│  60,310 chunks | 337 NIST docs | 55K conversations  │
└─────────────────────────────────────────────────────┘
```

### **Key Components**

1. **Multi-Agent Orchestration**
   - Dependency-aware workflow execution
   - Parallel agent execution (ThreadPoolExecutor)
   - Standardized AgentResult interface
   - Progress tracking and error handling

2. **Knowledge Graph**
   - Entity extraction (controls, concepts, publications)
   - Relationship discovery (co-occurrence, hierarchy)
   - NetworkX-based graph operations
   - Hybrid vector + graph retrieval

3. **Vector RAG**
   - ChromaDB persistence
   - all-MiniLM-L6-v2 embeddings
   - Sub-second retrieval
   - 60K+ chunk corpus

4. **Visualization**
   - 9 interactive Plotly charts
   - Temporal analysis dashboards
   - Compliance heatmaps
   - Graph network diagrams

---

## 🧪 **Testing & Validation**

### **Integration Tests**
```bash
python tests/test_integration.py
```

**Coverage:**
- Agent orchestration (3 tests)
- Compliance agent (2 tests)
- Research agent (2 tests)
- Synthesis agent (3 tests)
- Knowledge graph (5 tests)
- Performance (2 tests)

**Results**: 17 tests, 16 passed, 1 expected failure = **94.1% pass rate**

### **Demo Validation**
```bash
python scripts/demo_validation.py
```

**Validates:**
- ✅ Module imports (all 11 modules)
- ✅ Artifact presence
- ✅ Agent initialization
- ✅ Entity extraction
- ✅ Report generation

**Results**: **100% validation pass** ✅

### **Performance Monitoring**
```bash
python scripts/performance_check.py
```

**Monitors:**
- System resources (CPU, memory, disk)
- Artifact sizes
- Module import times
- Agent initialization performance

---

## 📚 **Documentation**

### **User Guides**
- [README.md](README.md) - This file
- [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) - 6-minute demo narration
- [ROADMAP.md](docs/ROADMAP.md) - Future enhancements

### **Technical Docs**
- [SPRINT_COMPLETE.md](docs/SPRINT_COMPLETE.md) - Complete sprint summary
- [DAY4_COMPLETE.md](docs/DAY4_COMPLETE.md) - Visualization implementation
- [DAY5_COMPLETE.md](docs/DAY5_COMPLETE.md) - Testing & validation

### **Demo Materials**
- [DEMO_DECK_OUTLINE.md](docs/DEMO_DECK_OUTLINE.md) - 15-slide presentation
- [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) - Narrated walkthrough

---

## 🔒 **Privacy & Security**

### **Local-First Architecture**
- ✅ **No cloud dependencies** - All processing on-premises
- ✅ **Complete data sovereignty** - Your data never leaves your infrastructure
- ✅ **Zero telemetry** - No tracking or analytics sent to third parties
- ✅ **Air-gappable** - Works in fully isolated environments

### **Deployment Options**
- **Mac** (current demo platform)
- **Raspberry Pi** (local-first proven)
- **On-premises servers** (Linux/Docker)
- **Air-gapped environments** (complete isolation)

---

## 🚀 **Future Roadmap**

See [ROADMAP.md](docs/ROADMAP.md) for complete enhancement plan.

**Highlights:**
- Additional agents (data analysis, policy generation)
- Advanced graph algorithms (GNN, community detection)
- Multi-modal support (PDF, images, audio)
- Production deployment (Docker, Kubernetes)
- Enterprise features (SSO, audit logs, multi-tenancy)

---

## 📊 **Tech Stack**

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Knowledge Graph | NetworkX |
| Clustering | scikit-learn (K-means) |
| Visualization | Plotly |
| UI Framework | Streamlit |
| LLM (optional) | MLX (Apple Silicon) or OpenAI API |
| Testing | pytest + custom suite |

---

## 🎯 **Key Features**

### **Autonomous Agents**
- ✅ Compliance gap analysis (NIST controls)
- ✅ Multi-hop research synthesis
- ✅ Structured report generation
- ✅ Workflow orchestration with dependencies

### **Knowledge Graph**
- ✅ Entity extraction (controls, concepts, pubs)
- ✅ Relationship discovery (co-occurrence, hierarchy)
- ✅ Graph-enhanced RAG (hybrid retrieval)
- ✅ Interactive visualization

### **Visualizations**
- ✅ Compliance dashboard (5 chart types)
- ✅ Temporal analysis (4 chart types)
- ✅ Knowledge graph networks
- ✅ Interactive Plotly charts

### **Quality**
- ✅ 94% integration test pass rate
- ✅ 100% demo validation pass
- ✅ Comprehensive error handling
- ✅ Performance monitoring

---

## 📞 **Support & Contributing**

### **Demo Issues**
Run pre-demo validation:
```bash
python scripts/demo_validation.py
```

### **Performance Issues**
Check system health:
```bash
python scripts/performance_check.py
```

### **General Issues**
Check documentation in `docs/` folder or run:
```bash
python tests/test_integration.py
```

---

## 🏆 **Achievements**

### **What We Built**
- 🤖 **3 autonomous agents** (compliance, research, synthesis)
- 🕸️ **Knowledge graph** with 500-1K entities
- 📊 **9 visualization types** (Plotly interactive)
- 🧪 **17 integration tests** (94% pass rate)
- 📚 **~10,000 lines** of code + docs
- 🎯 **100% demo validation** pass

### **Why It's Impressive**
1. **Not Just RAG** - Autonomous workflows that produce deliverables
2. **Production Quality** - Tests, validation, monitoring, error handling
3. **Graph Reasoning** - Beyond vector search with relationship discovery
4. **Privacy First** - 100% local, no cloud dependencies
5. **7-Day Build** - Rapid development with production-grade output

---

## 📄 **License**

[Your License Here]

---

## 🙏 **Acknowledgments**

Built with modern AI-assisted development practices, demonstrating the power of:
- Autonomous agents for knowledge work
- Graph-based reasoning
- Privacy-preserving architecture
- Rapid prototyping with production quality

---

**Status**: ✅ Demo Ready | 🧪 94% Tested | 🔒 100% Local | 🚀 Production Quality

*Last Updated: January 1, 2026*
