import argparse
from pathlib import Path
import pandas as pd
from rich import print

def parse_with_unstructured(pdf_path: Path):
    try:
        from unstructured.partition.pdf import partition_pdf
        elements = partition_pdf(str(pdf_path))
        rows = []
        for el in elements:
            text = getattr(el, "text", "") or ""
            if not text.strip():
                continue
            meta = {
                "category": getattr(el, "category", None),
                "source": pdf_path.name
            }
            rows.append({"text": text, "page": getattr(el, "page_number", None), "source": pdf_path.name, "meta": meta})
        return rows
    except Exception as e:
        print(f"[yellow]unstructured failed on {pdf_path}: {e}. Falling back to PyMuPDF.[/yellow]")
        return parse_with_pymupdf(pdf_path)

def parse_with_pymupdf(pdf_path: Path):
    import fitz  # PyMuPDF
    rows = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text and text.strip():
                rows.append({"text": text, "page": i, "source": pdf_path.name, "meta": {"category": "Page", "source": pdf_path.name}})
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nist", type=str, default="data/nist", help="NIST PDFs dir")
    ap.add_argument("--iapp", type=str, default="data/iapp", help="IAPP PDFs dir")
    ap.add_argument("--out", type=str, required=True, help="Output Parquet path")
    args = ap.parse_args()

    rows = []
    for folder in [Path(args.nist), Path(args.iapp)]:
        if not folder.exists():
            continue
        for pdf in folder.glob("*.pdf"):
            rows += parse_with_unstructured(pdf)

    df = pd.DataFrame(rows)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"[green]Wrote {len(df)} rows to {out}[/green]")

if __name__ == "__main__":
    main()
