import argparse, json
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

def chunk_text(text, chunk_size=800, overlap=120):
    # simple whitespace-based chunker (token-agnostic)
    words = text.split()
    if not words:
        return []
    chunks, i = [], 0
    step = max(1, chunk_size - overlap)
    while i < len(words):
        chunk = words[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += step
    return chunks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True, help="Input parquet(s)")
    ap.add_argument("--persist", required=True, help="Chroma persist dir")
    ap.add_argument("--name", default="studykit", help="Collection name")
    ap.add_argument("--chunk-size", type=int, default=800)
    ap.add_argument("--overlap", type=int, default=120)
    args = ap.parse_args()

    frames = [pd.read_parquet(p) for p in args.inputs]
    df = pd.concat(frames, ignore_index=True)

    # Normalize expected columns
    if "text" not in df.columns:
        if "content" in df.columns:
            df["text"] = df["content"].astype(str)
        else:
            df["text"] = ""
    if "source" not in df.columns:
        df["source"] = None
    if "page" not in df.columns:
        df["page"] = None

    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = PersistentClient(path=args.persist)
    coll = client.get_or_create_collection(args.name)

    ids, docs, metas, embs = [], [], [], []
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        text = str(row["text"])
        if not text.strip():
            continue
        for chunk in chunk_text(text, args.chunk_size, args.overlap):
            doc_id = f"r{idx}-c{len(ids)}"
            ids.append(doc_id)
            docs.append(chunk)
            metas.append({"source": row.get("source"), "page": int(row.get("page")) if row.get("page") else None})
            # embed per chunk
            emb = model.encode([chunk])[0].tolist()
            embs.append(emb)

    # Add in manageable batches
    B = 128
    for i in range(0, len(ids), B):
        coll.add(ids=ids[i:i+B], documents=docs[i:i+B], metadatas=metas[i:i+B], embeddings=embs[i:i+B])

    print(f"Indexed {len(ids)} chunks into '{args.name}' at {args.persist}")

if __name__ == "__main__":
    main()
