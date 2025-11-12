# Operations Playbook

## First-time setup
1) `make install`
2) Create `.env` from `.env.example` and adjust paths.

## Data bootstrap (optional)
- Put your ChatGPT export zip into `store/ChatGPT.zip` and run:
  ```bash
  python src/utils/bootstrap_data.py --openai-zip store/ChatGPT.zip
  ```
- Put NIST PDFs into `store/nist/` and IAPP PDFs into `store/iapp/`, then run:
  ```bash
  python src/utils/bootstrap_data.py --nist store/nist --iapp store/iapp
  ```

## Routine run
```bash
make ingest-openai ingest-pdfs index query
```

---

## UI quickstart

### Streamlit
```bash
make ui-streamlit
```

### Gradio
```bash
make ui-gradio
```

## Build SFT dataset from your Chat export
```bash
python src/utils/make_sft.py --openai-parquet artifacts/openai.parquet --out artifacts/sft.jsonl
```
