import argparse, zipfile, shutil
from pathlib import Path

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--openai-zip", type=str, help="Path to ChatGPT export zip")
    ap.add_argument("--nist", type=str, help="Directory of NIST PDFs")
    ap.add_argument("--iapp", type=str, help="Directory of IAPP PDFs")
    ap.add_argument("--out-openai", type=str, default="data/openai")
    ap.add_argument("--out-nist", type=str, default="data/nist")
    ap.add_argument("--out-iapp", type=str, default="data/iapp")
    args = ap.parse_args()

    if args.openai_zip:
        out = Path(args.out_openai); ensure_dir(out)
        with zipfile.ZipFile(args.openai_zip, "r") as z:
            z.extractall(out)
        print(f"Extracted ChatGPT export to {out}")

    if args.nist:
        src = Path(args.nist); dst = Path(args.out_nist); ensure_dir(dst)
        for p in src.glob("*.pdf"):
            shutil.copy2(p, dst / p.name)
        print(f"Copied NIST PDFs to {dst}")

    if args.iapp:
        src = Path(args.iapp); dst = Path(args.out_iapp); ensure_dir(dst)
        for p in src.glob("*.pdf"):
            shutil.copy2(p, dst / p.name)
        print(f"Copied IAPP PDFs to {dst}")

if __name__ == "__main__":
    main()
