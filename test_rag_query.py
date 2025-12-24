#!/usr/bin/env python3
"""
Quick RAG testing script to validate the pipeline
"""
import os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

def test_query(question, k=6):
    """Test a single RAG query"""
    print(f"\n{'='*80}")
    print(f"QUESTION: {question}")
    print(f"{'='*80}\n")

    # Load components
    print("Loading embedding model...")
    embed = SentenceTransformer("all-MiniLM-L6-v2")

    print("Connecting to ChromaDB...")
    client = PersistentClient(path="artifacts/index")
    coll = client.get_collection("studykit")

    # Query
    print(f"Searching for top {k} passages...")
    qv = embed.encode([question])[0].tolist()
    r = coll.query(query_embeddings=[qv], n_results=k)

    chunks = r["documents"][0]
    metas = r["metadatas"][0]

    # Display results
    print("\n--- RETRIEVED PASSAGES ---\n")
    for i, (chunk, meta) in enumerate(zip(chunks, metas), start=1):
        source = meta.get('source', 'unknown')
        page = meta.get('page', 0)

        # Determine source type
        if 'NIST' in str(source).upper() or '.pdf' in str(source).lower():
            source_type = "📄 NIST"
        else:
            source_type = "💬 Chat"

        print(f"[{i}] {source_type} | source={source} | page={page}")
        print(f"    {chunk[:200]}..." if len(chunk) > 200 else f"    {chunk}")
        print()

    return chunks, metas

if __name__ == "__main__":
    # Test queries

    # Test 1: NIST-focused query
    test_query("What is the current guidance around establishing digital identity?", k=6)

    # Test 2: Personal conversation query
    test_query("What are the main AI topics I've explored in my conversations?", k=8)

    # Test 3: General query
    test_query("Summarize my thoughts on privacy and security", k=6)

    print("\n" + "="*80)
    print("RAG PIPELINE TEST COMPLETE")
    print("="*80)
