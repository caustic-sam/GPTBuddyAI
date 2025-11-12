import argparse, json, pandas as pd
from pathlib import Path

def from_openai_parquet(parquet_path: Path):
    df = pd.read_parquet(parquet_path)
    # Heuristic: rows with author "user" followed by "assistant" in same conversation become pairs
    cols = {c.lower(): c for c in df.columns}
    def col(name): return cols.get(name, name)
    if "author" not in cols or "text" not in cols:
        raise ValueError("Expected 'author' and 'text' columns in parquet.")
    if "conversation_id" not in cols:
        df["conversation_id"] = "unknown"
    df = df.sort_values([col("conversation_id"), col("create_time")], na_position="first")
    pairs = []
    last_user = None
    last_cid = None
    for _, r in df.iterrows():
        author = str(r[col("author")])
        text = str(r[col("text")])
        cid = r[col("conversation_id")]
        if author == "user":
            last_user = text
            last_cid = cid
        elif author == "assistant" and last_user is not None and last_cid == cid:
            pairs.append({"prompt": last_user, "response": text})
            last_user = None
    return pairs

def from_csv(csv_path: Path):
    # CSV with columns: prompt,response
    import csv
    pairs = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            pairs.append({"prompt": row["prompt"], "response": row["response"]})
    return pairs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--openai-parquet", type=str, help="artifacts/openai.parquet")
    ap.add_argument("--csv", type=str, help="optional curated QA CSV with columns prompt,response")
    ap.add_argument("--out", type=str, default="artifacts/sft.jsonl")
    args = ap.parse_args()

    records = []
    if args.openai_parquet:
        records += from_openai_parquet(Path(args.openai_parquet))
    if args.csv:
        records += from_csv(Path(args.csv))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} SFT records to {out}")

if __name__ == "__main__":
    main()
