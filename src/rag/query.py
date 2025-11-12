import argparse, os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from rich import print

def load_mlx_model():
    from mlx_lm import load
    model_id = os.getenv("LM_MODEL", "mlx-community/SmolLM2-1.7B-Instruct-4bit")
    return load(model_id)

def generate_mlx(model_tuple, prompt, max_tokens=400):
    from mlx_lm import generate
    model, tok = model_tuple
    return generate(model, tok, prompt, max_tokens=max_tokens)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", required=True, help="Question")
    ap.add_argument("--topk", type=int, default=6)
    ap.add_argument("--persist", default="artifacts/index")
    ap.add_argument("--name", default="studykit")
    ap.add_argument("--max-tokens", type=int, default=int(os.getenv("LM_MAX_TOKENS", "400")))
    args = ap.parse_args()

    client = PersistentClient(path=args.persist)
    coll = client.get_collection(args.name)
    embed = SentenceTransformer("all-MiniLM-L6-v2")

    qv = embed.encode([args.q])[0].tolist()
    r = coll.query(query_embeddings=[qv], n_results=args.topk)
    chunks = r["documents"][0]
    metas = r["metadatas"][0]

    context = ""
    for i, (c, m) in enumerate(zip(chunks, metas), start=1):
        cite = f"[{i}] source={m.get('source')} page={m.get('page')}"
        context += f"{cite}\n{c}\n\n"
    prompt = f"Use the CONTEXT to answer with inline citations like [1], [2].\n\nCONTEXT:\n{context}\nQ: {args.q}\nA:"

    model_tuple = load_mlx_model()
    out = generate_mlx(model_tuple, prompt, max_tokens=args.max_tokens)
    print(out)
    print("\nCitations:")
    for i, m in enumerate(metas, start=1):
        print(f"[{i}] {m.get('source')} (page {m.get('page')})")

if __name__ == "__main__":
    main()
