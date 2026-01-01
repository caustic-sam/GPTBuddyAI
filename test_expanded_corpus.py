#!/usr/bin/env python3
"""
Test RAG with expanded NIST corpus (337 documents)
"""
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

def test_nist_coverage(query, k=8):
    """Test NIST document retrieval"""
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}\n")

    # Load components
    embed = SentenceTransformer("all-MiniLM-L6-v2")
    client = PersistentClient(path="artifacts/index")
    coll = client.get_collection("studykit")

    # Query
    qv = embed.encode([query])[0].tolist()
    r = coll.query(query_embeddings=[qv], n_results=k)

    chunks = r["documents"][0]
    metas = r["metadatas"][0]

    # Analyze results
    nist_count = 0
    chat_count = 0
    sp_numbers = set()

    print("Retrieved passages:\n")
    for i, (chunk, meta) in enumerate(zip(chunks, metas), start=1):
        source = meta.get('source', 'unknown')
        page = meta.get('page', 0)

        is_nist = 'NIST' in str(source).upper() or '.pdf' in str(source).lower()

        if is_nist:
            nist_count += 1
            icon = "📄"
            # Extract SP number if available
            if 'sp_number' in meta:
                sp_numbers.add(meta['sp_number'])
        else:
            chat_count += 1
            icon = "💬"

        print(f"[{i}] {icon} {source} (page {page})")
        preview = chunk[:150].replace('\n', ' ')
        print(f"    {preview}...\n")

    print(f"{'='*80}")
    print(f"Results: {nist_count} NIST docs, {chat_count} Chat messages")
    if sp_numbers:
        print(f"SP Numbers: {', '.join(sorted(sp_numbers))}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    # Test 1: Specific NIST query
    test_nist_coverage("What are the requirements for multifactor authentication?", k=8)

    # Test 2: Digital identity (your example)
    test_nist_coverage("What is the current guidance around establishing digital identity?", k=8)

    # Test 3: Zero trust architecture
    test_nist_coverage("Explain zero trust architecture principles", k=8)

    # Test 4: Supply chain security
    test_nist_coverage("What are NIST recommendations for supply chain risk management?", k=8)

    # Test 5: Cross-corpus query
    test_nist_coverage("How should I implement privacy controls?", k=8)

    print("\n" + "="*80)
    print("EXPANDED CORPUS TEST COMPLETE")
    print("="*80)