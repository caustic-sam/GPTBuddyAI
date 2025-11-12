import argparse, json, re
from pathlib import Path
import pandas as pd
from rich import print

def flatten_mapping(mapping):
    # Old ChatGPT export: a DAG keyed by message id
    rows = []
    for mid, node in mapping.items():
        msg = node.get("message") or {}
        author = (msg.get("author") or {}).get("role")
        content = ""
        if msg.get("content"):
            if isinstance(msg["content"], dict) and msg["content"].get("parts"):
                content = "\n".join(msg["content"]["parts"])
            elif isinstance(msg["content"], str):
                content = msg["content"]
        rows.append({
            "conversation_id": None,
            "message_id": mid,
            "author": author,
            "content": content,
            "create_time": msg.get("create_time"),
            "metadata": msg.get("metadata", {}),
            "source": "openai_export_mapping"
        })
    return rows

def load_any_json(path: Path):
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    rows = []
    if isinstance(data, dict) and "messages" in data:
        # Simple schema
        for m in data["messages"]:
            rows.append({
                "conversation_id": m.get("conversation_id"),
                "message_id": m.get("id"),
                "author": m.get("role") or (m.get("author") or {}).get("role"),
                "content": m.get("content") if isinstance(m.get("content"), str) else (m.get("content") or {}).get("parts", [""])[0],
                "create_time": m.get("create_time") or m.get("created_at"),
                "metadata": m.get("metadata") or {},
                "source": path.name
            })
    elif isinstance(data, list):
        # conversations.json style: list of conv objects
        for conv in data:
            cid = conv.get("id") or conv.get("conversation_id")
            title = conv.get("title")
            mapping = conv.get("mapping") or {}
            rows += [{**r, "conversation_id": cid, "conversation_title": title} for r in flatten_mapping(mapping)]
    elif isinstance(data, dict) and "mapping" in data:
        rows += flatten_mapping(data["mapping"])
    else:
        # fallback: treat as one message
        rows.append({"conversation_id": None, "message_id": None, "author": None, "content": json.dumps(data), "create_time": None, "metadata": {}, "source": path.name})
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input_path", required=True, help="Path to OpenAI export dir or JSON")
    ap.add_argument("--out", required=True, help="Output Parquet path")
    args = ap.parse_args()

    in_path = Path(args.input_path)
    rows = []
    if in_path.is_dir():
        for p in in_path.rglob("*.json"):
            try:
                rows += load_any_json(p)
            except Exception as e:
                print(f"[yellow]Skipping {p}: {e}[/yellow]")
    else:
        rows += load_any_json(in_path)

    import pandas as pd
    df = pd.DataFrame(rows)
    if "content" in df.columns:
        df["text"] = df["content"].astype(str)
    else:
        df["text"] = ""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"[green]Wrote {len(df)} rows to {out}[/green]")

if __name__ == "__main__":
    main()
