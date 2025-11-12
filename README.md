# GPTBuddyAI

GPTBuddyAI is a privacy-preserving analytics toolkit that turns exported AI chat archives into actionable insights. The project stitches together local language models, vector search, and a lightweight UI so you can summarize, tag, and explore your historical GPT conversations without sending data to the cloud. The repository ships with an opinionated roadmap, automation scripts, and GitHub project guidance so you can spin up a complete workflow—from ingestion through deployment on a Raspberry Pi—in roughly two weeks.

**New:** The toolkit now supports building a **comprehensive study and Q&A experience** by ingesting the **NIST SP 800** series and **IAPP** PDFs alongside your OpenAI export. You can generate citation-rich answers, synthesize study guides, and optionally fine-tune a small local LLM on Apple Silicon, with the option to convert to **Core ML** for on-device apps.

## Why GPTBuddyAI?
- Work entirely offline to keep sensitive conversations private.
- Rapidly surface trends, tags, and summaries across thousands of chats.
- Use semantic search and visualizations to rediscover past ideas.
- Deploy the full stack (data pipeline, embeddings, UI, and vector store) on modest hardware.
- **Compliance/Study Mode:** Ask questions across **OpenAI chats + NIST SP 800 + IAPP PDFs** with grounded, cited answers and auto-generated study notes.

## Core Features
- **Data ingestion & cleaning**: Parse OpenAI `conversations.json`, normalize metadata, and persist to SQLite or Parquet for reproducible downstream processing.
- **Multi-corpus ingestion (new)**: Structured PDF parsing for **NIST SP 800** and **IAPP** materials with page-level provenance for citations.
- **Summarization & tagging**: Leverage MLX-LM or a local LLM runner to generate concise summaries, tags, and entities per conversation or document.
- **Embedding pipeline**: Build dense vector representations with `sentence-transformers` and manage similarity search with Faiss or Chroma.
- **RAG Q&A (new)**: Retrieval-augmented generation over all corpora with inline citations and confidence/traceability metadata.
- **Study-guide synthesis (new)**: Auto-compose outlines, flashcards, and quick-reference sheets for exam prep and team enablement.
- **Apple Silicon first (new)**: Optional **MLX-LM** LoRA fine-tuning on-device and export to **Core ML** for Mac/iOS demos.
- **Interactive UI**: Ship a Streamlit or Gradio app featuring keyword + semantic search, filters, timeline charts, and detailed conversation drill-downs.
- **Deployment**: Containerize services and orchestrate them with Docker Compose on a Raspberry Pi, including watchdog scripts for headless operation.
- **Project operations**: GitHub Kanban workflow, templated issues, and documentation guardrails to keep the project moving smoothly.

## Reference Architecture
```
               ┌───────────────────────┐
               │  OpenAI Export (.zip) │
               └──────────┬────────────┘
                          │
     ┌────────────────────┼─────────────────────┐
     │                    │                     │
     ▼                    ▼                     ▼
┌─────────────┐     ┌─────────────┐       ┌─────────────┐
│  NIST SP800 │     │    IAPP     │       │ Other PDFs  │ (optional)
│     PDFs    │     │    PDFs     │       └─────────────┘
└─────┬───────┘     └─────┬───────┘
      │                   │
      └──────────┬────────┘
                 ▼
       ┌───────────────────────┐
       │ Ingestion & Cleaning  │  (PDF/JSON → structured text + metadata)
       └──────────┬────────────┘
                  ▼
         ┌─────────────────┐
         │  Vectorization  │  (sentence-transformers)
         └────────┬────────┘
                  ▼
        ┌────────────────────┐
        │ Vector DB (Faiss/  │
        │  Chroma/Qdrant)    │
        └────────┬───────────┘
                 ▼
     ┌──────────────────────────────┐
     │ RAG Q&A + Study Guide Synth  │  (citations, flashcards, outlines)
     └────────┬─────────────────────┘
              ▼
     ┌──────────────────────────────┐
     │ Local LLM Runtime            │  MLX-LM / LM Studio
     └────────┬─────────────────────┘
              ▼
     ┌──────────────────────────────┐
     │    UI (Streamlit/Gradio)     │
     └──────────────────────────────┘

(Optional path for productization)
Local LLM/LoRA  ──► Core ML convert ──► Swift/macOS or iOS app
```

## Project Structure
```
GPTBuddyAI/
├── data/
│   ├── openai/          # OpenAI chat export (JSON/zip)
│   ├── nist/            # NIST SP 800 PDFs
│   └── iapp/            # IAPP PDFs (licensed; keep private)
├── artifacts/
│   ├── embeddings/      # Numpy/Parquet embeddings
│   └── index/           # Vector DB persistence (Chroma/Faiss)
├── src/
│   ├── ingest/          # ingest_openai.py, ingest_pdfs.py
│   ├── rag/             # build_index.py, query.py, study_guide.py
│   ├── llm/             # mlx_finetune.py, coreml_export.py (optional)
│   └── ui/              # streamlit_app.py or gradio_app.py
├── docs/
│   ├── kanban-board.md
│   ├── issue-backlog.md
│   ├── operations-playbook.md
│   └── roadmap.md
├── workflows/           # future CI/CD (e.g., nightly ETL check)
├── .gitignore
└── README.md
```

## Local Environment Setup
1. **Clone** (after you create the remote repository):
   ```bash
   git clone git@github.com:<your-username>/GPTBuddyAI.git
   cd GPTBuddyAI
   ```
2. **Create Python environment** (3.10 or newer recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   ```
3. **Install project dependencies**:
   ```bash
   # Core stack
   pip install -r requirements.txt  # (create from docs/operations-playbook.md)
   # or explicitly:
   pip install sentence-transformers chromadb faiss-cpu pypdf pymupdf unstructured[all-docs]                streamlit gradio

   # Local LLM options
   pip install mlx-lm               # Apple MLX runtime + simple finetune utilities
   pip install coremltools          # Optional: export to Core ML for Apple platforms
   # Optional alternative runtime:
   # - LM Studio (macOS app) + a local GGUF model like mistral-7b-instruct
   ```
4. **Install platform tooling**:
   - **macOS**: Xcode Command Line Tools, Homebrew (for cmake/pkg-config if needed).
   - **Docker Desktop** (local builds) or Docker Engine on Raspberry Pi.
   - Optional: **JupyterLab** for quick experiments.
5. **Configure environment variables** in a `.env` file (not committed):
   ```dotenv
   DATA_DIR=~/data/gptbuddyai
   DATA_OPENAI=./data/openai
   DATA_NIST=./data/nist
   DATA_IAPP=./data/iapp

   VECTOR_BACKEND=chroma                 # or faiss
   VECTOR_PERSIST=./artifacts/index

   LM_RUNTIME=mlx                        # mlx | lmstudio
   LM_STUDIO_API=http://localhost:1234/v1  # if LM_RUNTIME=lmstudio

   RAG_CHUNK_SIZE=800
   RAG_CHUNK_OVERLAP=120
   ```

## Data Preparation
- **OpenAI export**: Drop the downloaded `.json`/folder into `data/openai/`.
- **NIST SP 800**: Place official PDFs in `data/nist/` (final publications preferred).
- **IAPP**: Place your licensed PDFs in `data/iapp/`. Keep usage internal; do not redistribute.

> **Licensing note:** NIST publications are generally public domain; IAPP materials are proprietary and should remain private and unshared.

## Ingestion & Indexing
Typical sequence (scripts live under `src/`):

```bash
# 1) Parse OpenAI export → normalized records
python src/ingest/ingest_openai.py --in $DATA_OPENAI --out ./artifacts/openai.parquet

# 2) Parse PDFs (NIST/IAPP) → structured text with metadata (page, section, source)
python src/ingest/ingest_pdfs.py --nist $DATA_NIST --iapp $DATA_IAPP --out ./artifacts/docs.parquet

# 3) Build or refresh embeddings + vector index
python src/rag/build_index.py --inputs ./artifacts/*.parquet --persist $VECTOR_PERSIST
```

## Ask Questions & Generate Study Guides
- **Ad-hoc query with citations**:
  ```bash
  python src/rag/query.py --q "Summarize AC-2 in NIST 800-53r5 and list key controls." --topk 6
  ```
- **Study-guide synthesis** (outline + flashcards from top-k context):
  ```bash
  python src/rag/study_guide.py --topic "IAPP privacy principles vs. NIST access controls" --pages 2
  ```

Both scripts retrieve relevant chunks from the vector DB and then call a **local LLM**:
- **Default**: `mlx-lm` model (e.g., `mlx-community/SmolLM2-1.7B-Instruct-4bit`)
- **Alternate**: LM Studio via `LM_STUDIO_API`.

## Optional: Apple-Native Fine-Tuning & Core ML Export
- **Light LoRA on Apple Silicon** to align tone/format for compliance Q&A:
  ```bash
  mlx_lm.finetune     --model mlx-community/SmolLM2-1.7B-Instruct-4bit     --train-data ./artifacts/sft.jsonl     --lora-rank 8 --batch-size 8 --epochs 3 --lr 2e-4     --save-adapter ./artifacts/lora
  ```
- **Core ML export** (prototype path; details vary by base model):
  ```bash
  python src/llm/coreml_export.py --in ./artifacts/model --out ./artifacts/StudyKit-LLM.mlpackage
  ```
Use the Core ML package in a Swift macOS/iOS demo for fully on-device inference.

## GitHub Repository Setup
Use these steps the first time you publish the project:
```bash
# inside /Users/jm/myProjects
mv GPTBuddyAI ~/Projects  # optional relocation
cd GPTBuddyAI
git init
printf "#.venv
__pycache__/
*.pyc
.env
*.egg-info/
dist/
build/
.DS_Store
" > .gitignore
git add .
git commit -m "chore: bootstrap GPTBuddyAI repo"
git remote add origin git@github.com:<your-username>/GPTBuddyAI.git
git branch -M main
git push -u origin main
```

## GitHub Project (Kanban) Configuration
1. Create a **GitHub Project (Beta)** named `GPTBuddyAI` attached to the repository.
2. Define columns (Kanban) and policies:
   - `Backlog` – Intake for new work; no WIP limit.
   - `Ready` – Groomed issues with acceptance criteria; WIP limit 7.
   - `In Progress` – Active development; WIP limit 4.
   - `Review` – Awaiting PR review, QA, or validation.
   - `Done` – Completed and deployed tasks.
3. Add views/fields:
   - Custom fields: `Priority` (P0–P3), `Milestone`, `Target Release`.
   - Saved views: "Sprint Board" (filter by open, milestone), "Icebox" (Backlog + P3).
4. Enable auto-linking of issues by referencing them in pull requests (PR template TBD).
5. Automate board hygiene with weekly `gh projectitem-update` job (workflow stub in `workflows/`).

## Seed Issues
| Title | Description | Priority | Labels |
| --- | --- | --- | --- |
| Data Parsing Pipeline | Load `conversations.json`, normalize fields, and persist to SQLite/Parquet. Include unit tests for malformed records. | P0 | `area:data`, `type:feature` |
| PDF Ingestion (NIST/IAPP) | Robust PDF → structured text with page/section metadata; provenance preserved for citations. | P0 | `area:data`, `type:feature` |
| RAG Index & Retrieval | Build embeddings, stand up Faiss/Chroma, implement hybrid search and top-k reranking. | P0 | `area:data`, `type:feature` |
| Q&A Service | Expose a RAG endpoint with citation payloads and confidence. | P1 | `area:llm`, `type:feature` |
| Study-Guide Generator | Outline + flashcards from retrieved context; export to Markdown/PDF. | P1 | `area:llm`, `type:feature` |
| Local LLM Runtime | Wire MLX-LM default model; fallback to LM Studio if configured. | P1 | `area:llm`, `type:feature` |
| LoRA Fine-Tune (Optional) | Prepare `sft.jsonl` from Q↔A transcripts; run LoRA on Apple Silicon. | P2 | `area:llm`, `type:feature` |
| Core ML Demo (Optional) | Convert model to Core ML and build a minimal Swift app (macOS). | P2 | `area:ops`, `type:task` |
| UI Skeleton | Streamlit/Gradio search + detail + study-guide views; cite sources inline. | P1 | `area:ui`, `type:feature` |
| Deployment Baseline | Dockerfiles/Compose for API, UI, vector DB; smoke test on Raspberry Pi. | P1 | `area:ops`, `type:task` |
| Analytics Dashboards | Time-series charts and usage analytics embedded in the UI. | P2 | `area:ui`, `type:feature` |
| Documentation | Maintain setup guides and architecture notes in `docs/`. | P2 | `type:doc` |

## Two-Week MVP Roadmap
- **Days 1–2 – Setup & Multi-Corpus Ingestion**
  - Initialize repo/venv, finalize `.env`, ingest OpenAI export, NIST SP 800 PDFs, and IAPP PDFs.
  - Enable Kanban board, labels, and issue templates.
- **Days 3–4 – Summaries & Tagging**
  - Install LM runtime (MLX-LM or LM Studio); iterate on prompts; batch-generate summaries/tags.
- **Days 5–6 – Embeddings & Vector Index**
  - Create embeddings; evaluate retrieval on a test set (NIST controls, IAPP principles).
- **Days 7–9 – RAG Q&A + UI Skeleton**
  - Implement Q&A with citations; wire UI (search, filters, doc viewer).
- **Days 10–11 – Study-Guide Synth + Evaluation**
  - Generate outlines/flashcards; manual QA against known answers.
- **Days 12–14 – Deployment & Polish**
  - Containerize, smoke test on Raspberry Pi; refine prompts, performance, and docs.

## Documentation & Operational Playbook
- `docs/roadmap.md`: Milestones and acceptance criteria per phase.
- `docs/kanban-board.md`: Board definitions, WIP policies, and automation tips.
- `docs/issue-backlog.md`: Copy-ready issues with acceptance criteria.
- `docs/operations-playbook.md`: Environment variables, ingestion/run commands, monitoring tips, and rollback plans. Include licensing reminders for IAPP materials.

## Automation Hooks
- `workflows/` reserved for GitHub Actions (e.g., nightly ETL smoke test, dependency audit).
- Future scripts:
  - `scripts/bootstrap_data.sh` – create folders, verify `.env`, quick sanity checks.
  - `scripts/run_vector_tests.py` – retrieval quality harness.
  - `scripts/deploy_pi.sh` – Compose deployment and health checks.

## Contribution Guidelines (Draft)
- Prefer feature branches named `feature/<short-desc>`.
- Require PR review + CI green before merging to `main`.
- Document prompt changes and model versions in `docs/changelog.md`.
- Follow semantic commit messages (`type(scope): summary`).

## Licensing
Choose a license that matches your distribution goals (e.g., MIT, Apache-2.0). Add `LICENSE` before first public release.
- **Data**: Keep IAPP content private and non-redistributable. NIST publications are generally public domain; verify specific documents.

---
**Next Steps**
1. Drop your OpenAI export and PDFs into `data/` as noted above.
2. Wire `.env` and run the ingestion/index scripts.
3. Spin up the UI and test questions across all corpora; iterate on prompts and chunking parameters.
4. (Optional) Try LoRA on MLX-LM; if you like the results, export to Core ML and demo a Swift app.
