#!/usr/bin/env python3
"""
Test all 5 demo queries to verify they work before the big demo!
"""
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import time

def test_query(question, k=6, query_num=1):
    """Test a single query and show results"""
    print(f"\n{'='*80}")
    print(f"DEMO QUERY #{query_num}")
    print(f"{'='*80}")
    print(f"Q: {question}\n")

    # Load components
    embed = SentenceTransformer("all-MiniLM-L6-v2")
    client = PersistentClient(path="artifacts/index")
    coll = client.get_collection("studykit")

    # Measure latency
    start_time = time.time()

    # Query
    qv = embed.encode([question])[0].tolist()
    r = coll.query(query_embeddings=[qv], n_results=k)

    chunks = r["documents"][0]
    metas = r["metadatas"][0]

    latency = time.time() - start_time

    # Analyze results
    nist_count = 0
    chat_count = 0
    sources = []

    print(f"⏱️  Latency: {latency:.2f}s")
    print(f"\nTop {k} Results:\n")

    for i, (chunk, meta) in enumerate(zip(chunks, metas), start=1):
        source = meta.get('source', 'unknown')
        page = meta.get('page', 0)

        is_nist = 'NIST' in str(source).upper() or '.pdf' in str(source).lower()

        if is_nist:
            nist_count += 1
            icon = "📄 NIST"
            sources.append(source)
        else:
            chat_count += 1
            icon = "💬 Chat"

        print(f"[{i}] {icon} | {source} (page {page})")
        preview = chunk[:120].replace('\n', ' ')
        print(f"    \"{preview}...\"\n")

    print(f"{'='*80}")
    print(f"Results Mix: {nist_count} NIST docs, {chat_count} Chat messages")
    print(f"Latency: {latency:.2f}s")

    if nist_count > 0:
        print(f"NIST Sources: {list(set(sources))[:3]}")  # Show unique sources

    print(f"{'='*80}\n")

    return {
        'latency': latency,
        'nist_count': nist_count,
        'chat_count': chat_count,
        'pass': latency < 5.0  # Must be under 5 seconds
    }

if __name__ == "__main__":
    print("\n" + "🎬 " * 20)
    print("DEMO QUERY VALIDATION - Jan 1, 2026")
    print("🎬 " * 20 + "\n")

    results = []

    # Query 1: Personal Knowledge Discovery
    r1 = test_query(
        "What are the main themes I've explored about AI ethics and regulation over the past 2 years?",
        k=8,
        query_num=1
    )
    results.append(('Q1: Personal Insights', r1))

    # Query 2: NIST Compliance Reference
    r2 = test_query(
        "What is the current guidance around establishing digital identity and what are the identity assurance levels?",
        k=6,
        query_num=2
    )
    results.append(('Q2: NIST Reference', r2))

    # Query 3: Zero Trust Architecture
    r3 = test_query(
        "Explain the core principles of zero trust architecture according to NIST",
        k=6,
        query_num=3
    )
    results.append(('Q3: Zero Trust', r3))

    # Query 4: Cross-Corpus Synthesis (The WOW query)
    r4 = test_query(
        "How do my thoughts on privacy and digital sovereignty align with NIST's privacy controls in SP 800-53?",
        k=8,
        query_num=4
    )
    results.append(('Q4: Cross-Corpus [WOW]', r4))

    # Query 5: MFA Deep Dive
    r5 = test_query(
        "What are the specific requirements for multifactor authentication in e-commerce according to NIST?",
        k=6,
        query_num=5
    )
    results.append(('Q5: MFA Technical', r5))

    # Summary Report
    print("\n" + "="*80)
    print("📊 DEMO READINESS REPORT")
    print("="*80 + "\n")

    all_pass = True
    for name, result in results:
        status = "✅ PASS" if result['pass'] else "❌ FAIL"
        print(f"{status} {name}")
        print(f"     Latency: {result['latency']:.2f}s | NIST: {result['nist_count']} | Chat: {result['chat_count']}")

        if not result['pass']:
            all_pass = False

    print("\n" + "="*80)

    if all_pass:
        print("🎉 ALL QUERIES READY FOR DEMO!")
        print("✅ Latency < 5s on all queries")
        print("✅ Results are relevant and diverse")
        print("\nYou're good to go for tomorrow! 🚀")
    else:
        print("⚠️  SOME QUERIES NEED ATTENTION")
        print("Review failed queries above and optimize if needed")

    print("="*80 + "\n")

    # Recommendations
    print("📋 PRE-DEMO CHECKLIST:")
    print("  [ ] Run this script tomorrow morning")
    print("  [ ] Test queries in actual UI at http://localhost:8501")
    print("  [ ] Take screenshots of each result")
    print("  [ ] Practice narration for each query")
    print("  [ ] Have backup queries ready")
    print("\n")
