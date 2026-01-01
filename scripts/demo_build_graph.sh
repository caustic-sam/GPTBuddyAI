#!/bin/bash
# Demo script to build knowledge graph from existing ChromaDB collection

set -e

echo "🕸️ Building Knowledge Graph for GPTBuddyAI"
echo "============================================"
echo ""

# Check if ChromaDB index exists
if [ ! -d "artifacts/index" ]; then
    echo "❌ ChromaDB index not found at artifacts/index"
    echo "💡 Run: python src/rag/build_index.py first"
    exit 1
fi

# Create output directory
mkdir -p artifacts/graph

# Build graph with sample (faster for demo)
echo "📊 Building graph from 10,000 documents (sample)..."
python src/graph/build_knowledge_graph.py \
    --persist artifacts/index \
    --collection studykit \
    --output artifacts/graph/knowledge_graph.pkl \
    --sample 10000

echo ""
echo "✅ Knowledge graph built successfully!"
echo ""
echo "📍 Graph saved to: artifacts/graph/knowledge_graph.pkl"
echo "📊 Statistics saved to: artifacts/graph/graph_statistics.json"
echo ""
echo "🚀 Next steps:"
echo "  1. Refresh Streamlit app"
echo "  2. Navigate to '🕸️ Knowledge Graph' tab"
echo "  3. Explore entities, relationships, and visualizations"
echo ""
