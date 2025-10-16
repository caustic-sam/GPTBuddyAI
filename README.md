# GPTBuddyAI

GPTBuddyAI is a privacy-preserving analytics toolkit that turns exported AI chat archives into actionable insights. The project stitches together local language models, vector search, and a lightweight UI so you can summarize, tag, and explore your historical GPT conversations without sending data to the cloud. The repository ships with an opinionated roadmap, automation scripts, and GitHub project guidance so you can spin up a complete workflow—from ingestion through deployment on a Raspberry Pi—in roughly two weeks.

## Why GPTBuddyAI?
- Work entirely offline to keep sensitive conversations private.
- Rapidly surface trends, tags, and summaries across thousands of chats.
- Use semantic search and visualizations to rediscover past ideas.
- Deploy the full stack (data pipeline, embeddings, UI, and vector store) on modest hardware.

## Core Features
- **Data ingestion & cleaning**: Parse OpenAI `conversations.json`, normalize metadata, and persist to SQLite or Parquet for reproducible downstream processing.
- **Summarization & tagging**: Leverage LM Studio or another local LLM runner to generate concise summaries, tags, and entities for each conversation.
- **Embedding pipeline**: Build dense vector representations with `sentence-transformers` and manage similarity search with Faiss or Chroma.
- **Interactive UI**: Ship a Streamlit or Gradio app featuring keyword + semantic search, filters, timeline charts, and detailed conversation drill-downs.
- **Deployment**: Containerize services and orchestrate them with Docker Compose on a Raspberry Pi, including watchdog scripts for headless operation.
- **Project operations**: GitHub Kanban workflow, templated issues, and documentation guardrails to keep the project moving smoothly.

## Reference Architecture
```
┌─────────────────────┐      ┌──────────────────────┐
│ OpenAI Export (.zip)│      │  Metadata Catalog    │
└──────────┬──────────┘      └──────────┬───────────┘
           │                            │
           ▼                            ▼
 ┌──────────────────┐         ┌──────────────────────┐
 │ Data Ingestion & │  ETL    │ Summaries & Tagging  │
 │   Cleaning       │ ───────▶│ (LM Studio / LLM API)│
 └────────┬─────────┘         └──────────┬───────────┘
          │                              │
          ▼                              ▼
 ┌──────────────────┐         ┌──────────────────────┐
 │   SQLite /       │         │  Embedding Pipeline  │
 │   Parquet Store  │◀────────│ (sentence-transformers│
 └────────┬─────────┘  Vectors└──────────┬───────────┘
          │                              │
          ▼                              ▼
 ┌──────────────────┐         ┌──────────────────────┐
 │  Streamlit /     │◀────────│ Vector DB (Faiss/    │
 │  Gradio UI       │  Search │ Chroma / Qdrant)     │
 └────────┬─────────┘         └──────────┬───────────┘
          │                              │
          ▼                              ▼
 ┌──────────────────┐         ┌──────────────────────┐
 │ Analytics /      │         │ Deployment Targets   │
 │ Visualizations   │         │ (Docker + Raspberry Pi)│
 └──────────────────┘         └──────────────────────┘
```

## Project Structure
```
GPTBuddyAI/
├── .github/
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       ├── feature_request.md
│       ├── task.md
│       └── config.yml
├── docs/
│   ├── kanban-board.md        # Board columns, swimlanes, WIP policies, and usage tips
│   ├── issue-backlog.md       # Copy/paste issue seeds aligned to roadmap
│   ├── operations-playbook.md # Deployment, monitoring, and automation checklists
│   └── roadmap.md             # Two-week MVP plan with milestones and deliverables
├── workflows/                 # Reserved for future CI/CD pipelines (e.g., GitHub Actions)
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
   pip install -r requirements.txt  # create this from docs/operations-playbook.md guidance
   ```
3. **Install project tooling**:
   - LM Studio (macOS app) with a GGUF model such as `mistral-7b-instruct` or `deepseek-r1`.
   - Docker Desktop (for local builds) and/or Docker Engine on Raspberry Pi.
   - Optional: JupyterLab for rapid experimentation.
4. **Configure environment variables** in a `.env` file (not committed):
   ```dotenv
   DATA_DIR=~/data/gptbuddyai
   LM_STUDIO_API=http://localhost:1234/v1
   VECTOR_BACKEND=faiss  # or chroma
   STREAMLIT_AUTH_TOKEN=change-me
   ```

## GitHub Repository Setup
Use these steps the first time you publish the project:
```bash
# inside /Users/jm/myProjects
mv GPTBuddyAI ~/Projects  # optional relocation
cd GPTBuddyAI
git init
printf "#.venv\n__pycache__/\n*.pyc\n.env\n*.egg-info/\ndist/\nbuild/\n.DS_Store\n" > .gitignore
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
Replicate the following backlog (copy from `docs/issue-backlog.md`). Suggested labels: `area:data`, `area:llm`, `area:ui`, `priority:P0/P1/P2`, `type:feature`, `type:task`, `type:doc`.

| Title | Description | Priority | Labels |
| --- | --- | --- | --- |
| Data Parsing Pipeline | Stand up the ingestion module to load `conversations.json`, normalize fields, and persist to SQLite. Include unit tests for malformed records. | P0 | `area:data`, `type:feature` |
| Summarization Workflow | Integrate LM Studio API, craft prompts for conversation summarization, and store outputs alongside metadata. | P0 | `area:llm`, `type:feature` |
| Embedding Store | Generate sentence-transformer embeddings, stand up Faiss/Chroma index, and expose semantic search helpers. | P1 | `area:data`, `type:feature` |
| UI Skeleton | Prototype Streamlit UI with list, detail, and search components. Wire to mock data. | P1 | `area:ui`, `type:feature` |
| Deployment Baseline | Write Dockerfiles/Compose for API, UI, and vector services; smoke test on Raspberry Pi. | P1 | `area:ops`, `type:task` |
| Analytics Dashboards | Produce time-series charts and embed them in the UI. | P2 | `area:ui`, `type:feature` |
| Documentation | Maintain setup guides and architecture notes in Joplin + `docs/`. | P2 | `type:doc` |

## Two-Week MVP Roadmap
Timeline assumes Day 1 is the repository kickoff. Adjust dates in `docs/roadmap.md` to match your calendar.
- **Days 1–2 – Setup & Data Ingestion**
  - Initialize repo, stand up virtual env, parse `conversations.json`, publish stats.
  - Enable Kanban board, labels, and issue templates.
- **Days 3–4 – Summaries & Tagging**
  - Install LM Studio, iterate on prompts, batch-generate summaries/tags.
- **Days 5–6 – Embeddings & Vector Index**
  - Train/test embeddings, evaluate semantic search accuracy on sample queries.
- **Days 7–9 – UI Skeleton & Visualization**
  - Implement Streamlit or Gradio app with search, filters, timeline charts.
- **Days 10–11 – Deployment & Testing**
  - Containerize services, deploy to Raspberry Pi, validate performance.
- **Days 12–14 – Polish & Demo**
  - Harden pipelines, refine UI, capture demo artifacts, update docs.

## Documentation & Operational Playbook
- `docs/roadmap.md`: Expandable schedule with milestones, deliverable definition, and entry/exit criteria per phase.
- `docs/kanban-board.md`: Board column definitions, WIP policies, swimlanes, automation suggestions.
- `docs/issue-backlog.md`: Copy-ready issues with acceptance criteria to seed GitHub.
- `docs/operations-playbook.md`: Environment variables, deployment commands, monitoring tips, and rollback plans.

## Automation Hooks
- Placeholder directory `workflows/` for GitHub Actions (e.g., nightly ETL smoke test, dependency audit).
- Future scripts: `scripts/bootstrap_data.sh`, `scripts/run_vector_tests.py`, `scripts/deploy_pi.sh` (documented in `operations-playbook.md`).

## Contribution Guidelines (Draft)
- Prefer feature branches named `feature/<short-desc>`.
- Require PR review + CI green before merging to `main`.
- Document prompt changes and model versions in `docs/changelog.md` (to be created).
- Follow semantic commit messages (`type(scope): summary`).

## Licensing
Select a license that matches your distribution goals (e.g., MIT, Apache-2.0). Add `LICENSE` before first public release.

---
**Next Steps**
1. Populate `docs/` files (templates committed below) with project-specific details.
2. Create GitHub repository `GPTBuddyAI`, push this scaffold, and configure the project board.
3. Begin Day-1 tasks from the roadmap to build momentum toward the MVP.
