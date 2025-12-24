#!/usr/bin/env python3
"""
Bulk NIST PDF Ingestion Pipeline

Processes multiple NIST PDFs in parallel with:
- Automatic SP number extraction
- Quality validation
- Deduplication
- Progress tracking
"""
import argparse
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from tqdm import tqdm

# Try PyMuPDF first, fallback to unstructured
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    from unstructured.partition.pdf import partition_pdf

def extract_sp_number(filename):
    """Extract NIST SP number from filename"""
    # Common patterns:
    # - NIST.SP.800-53r5.pdf
    # - SP800-63-4.pdf
    # - 800-171r2.pdf

    patterns = [
        r'SP\.?[\s-]?(\d{3}-\d+[a-z]?\d*)',  # SP.800-53r5, SP 800-63-4
        r'NIST\.SP\.(\d{3}-\d+[a-z]?\d*)',   # NIST.SP.800-53r5
        r'(\d{3}-\d+[a-z]?\d*)',              # 800-171r2
    ]

    filename_upper = filename.upper()
    for pattern in patterns:
        match = re.search(pattern, filename_upper)
        if match:
            return f"SP {match.group(1)}"

    return None

def parse_nist_pdf_pymupdf(pdf_path):
    """Parse PDF using PyMuPDF (fast)"""
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if text.strip():
            pages.append({
                'page': page_num + 1,
                'text': text
            })

    doc.close()
    return pages

def parse_nist_pdf_unstructured(pdf_path):
    """Parse PDF using unstructured (fallback)"""
    elements = partition_pdf(str(pdf_path))
    pages = []

    for elem in elements:
        if hasattr(elem, 'metadata') and elem.metadata.page_number:
            page_num = elem.metadata.page_number
        else:
            page_num = 0

        pages.append({
            'page': page_num,
            'text': elem.text
        })

    return pages

def process_single_pdf(pdf_path, use_pymupdf=True):
    """Process a single NIST PDF"""
    try:
        filename = pdf_path.name
        sp_number = extract_sp_number(filename)

        if sp_number is None:
            sp_number = "Unknown"

        # Parse PDF
        if use_pymupdf and HAS_PYMUPDF:
            pages = parse_nist_pdf_pymupdf(pdf_path)
        else:
            pages = parse_nist_pdf_unstructured(pdf_path)

        if not pages:
            return None

        # Calculate quality score (% of pages with text)
        text_pages = sum(1 for p in pages if len(p['text'].strip()) > 100)
        quality_score = text_pages / len(pages) if pages else 0

        # Build records
        records = []
        for page_data in pages:
            records.append({
                'source': filename,
                'sp_number': sp_number,
                'page': page_data['page'],
                'text': page_data['text'],
                'content': page_data['text'],  # Alias for compatibility
            })

        return {
            'filename': filename,
            'sp_number': sp_number,
            'records': records,
            'quality_score': quality_score,
            'page_count': len(pages)
        }

    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")
        return None

def merge_with_existing(new_records, existing_parquet, output_parquet):
    """Merge new records with existing parquet, deduplicating"""

    if existing_parquet.exists():
        print(f"Loading existing data from {existing_parquet}")
        existing_df = pd.read_parquet(existing_parquet)
    else:
        existing_df = pd.DataFrame()

    new_df = pd.DataFrame(new_records)

    # Deduplicate by source filename
    if not existing_df.empty:
        new_sources = set(new_df['source'].unique())
        existing_df = existing_df[~existing_df['source'].isin(new_sources)]
        print(f"Removed {len(new_sources)} duplicate sources from existing data")

    # Merge
    merged_df = pd.concat([existing_df, new_df], ignore_index=True)

    # Save
    merged_df.to_parquet(output_parquet)
    print(f"Saved {len(merged_df)} total records to {output_parquet}")

    return merged_df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/nist", help="Directory with NIST PDFs")
    ap.add_argument("--output", default="artifacts/docs.parquet", help="Output parquet")
    ap.add_argument("--workers", type=int, default=4, help="Parallel workers")
    ap.add_argument("--quality-threshold", type=float, default=0.5, help="Min quality score (0-1)")
    args = ap.parse_args()

    input_dir = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Find all PDFs
    pdf_files = list(input_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files in {input_dir}")

    if not pdf_files:
        print("No PDFs found!")
        return

    # Process in parallel
    all_records = []
    successful = 0
    failed = 0

    print(f"\nProcessing with {args.workers} workers...")

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_single_pdf, pdf): pdf for pdf in pdf_files}

        for future in tqdm(as_completed(futures), total=len(pdf_files), desc="Processing PDFs"):
            result = future.result()

            if result is None:
                failed += 1
                continue

            if result['quality_score'] < args.quality_threshold:
                print(f"  ⚠️  {result['filename']}: Quality too low ({result['quality_score']:.1%}), skipping")
                failed += 1
                continue

            all_records.extend(result['records'])
            successful += 1
            print(f"  ✓ {result['filename']}: {result['page_count']} pages, SP {result['sp_number']}")

    print(f"\n{'='*80}")
    print(f"Processing complete: {successful} successful, {failed} failed/skipped")
    print(f"Total records: {len(all_records)}")
    print(f"{'='*80}\n")

    # Merge with existing
    if all_records:
        merged_df = merge_with_existing(all_records, output_path, output_path)

        # Summary by SP number
        print("\nDocuments by SP number:")
        sp_counts = merged_df.groupby('sp_number').size().sort_values(ascending=False)
        for sp, count in sp_counts.items():
            print(f"  {sp}: {count} pages")

        print(f"\n✅ Bulk ingestion complete!")
        print(f"   Run this to rebuild the index:")
        print(f"   python src/rag/build_index.py --inputs artifacts/openai.parquet artifacts/docs.parquet --persist artifacts/index --name studykit")

    else:
        print("No records to save")

if __name__ == "__main__":
    main()
