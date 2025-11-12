    import argparse, os
    from chromadb import PersistentClient
    from sentence_transformers import SentenceTransformer
    from mlx_lm import load, generate

    def main():
        ap = argparse.ArgumentParser()
        ap.add_argument("--topic", required=True)
        ap.add_argument("--pages", type=int, default=2, help="Approx pages of content to produce")
        ap.add_argument("--persist", default="artifacts/index")
        ap.add_argument("--name", default="studykit")
        args = ap.parse_args()

        client = PersistentClient(path=args.persist)
        coll = client.get_collection(args.name)
        embed = SentenceTransformer("all-MiniLM-L6-v2")

        q = f"Key points and definitions for: {args.topic}"
        qv = embed.encode([q])[0].tolist()
        r = coll.query(query_embeddings=[qv], n_results=12)
        chunks = r["documents"][0]
        metas = r["metadatas"][0]

        context = ""
        for i, (c, m) in enumerate(zip(chunks, metas), start=1):
            cite = f"[{i}] source={m.get('source')} page={m.get('page')}"
            context += f"{cite}\n{c}\n\n"

        model_id = os.getenv("LM_MODEL", "mlx-community/SmolLM2-1.7B-Instruct-4bit")
        model, tok = load(model_id)

        prompt = f"""You are a meticulous study-guide writer.
Use the CONTEXT to produce a {args.pages}-page equivalent study guide with:
- concise outline (bullets, nested)
- terminology/glossary
- 10 flashcards (Q/A)
- cite sources inline like [1] after sentences.

CONTEXT:
{context}

Study Guide:
"""
        out = generate(model, tok, prompt, max_tokens=1200)
        print(out)

    if __name__ == "__main__":
        main()
