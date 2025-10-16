# GPTBuddyAI Seed Issue Backlog

Use the following issue outlines to bootstrap the repository backlog. Copy each section into a new GitHub issue, apply the suggested labels, and link to relevant docs. The checklist format enforces acceptance criteria and encourages incremental PRs.

---

## 1. Data Parsing Pipeline
- **Labels**: `area:data`, `type:feature`, `priority:P0`
- **Description**:
  ```markdown
  ## Goal
  Load `conversations.json` exports, normalize metadata, and persist conversations to SQLite.

  ## Acceptance Criteria
  - [ ] CLI entry point `scripts/ingest_conversations.py` loads raw export path from CLI args.
  - [ ] Invalid/malformed records logged and skipped without crashing.
  - [ ] Output schema documented in `docs/operations-playbook.md`.
  - [ ] Unit tests cover at least two malformed payload scenarios.
  ```
- **Dependencies**: None
- **Milestone**: `MVP-Data`

## 2. Summarization Workflow
- **Labels**: `area:llm`, `type:feature`, `priority:P0`
- **Description**:
  ```markdown
  ## Goal
  Integrate LM Studio local API to summarize each conversation and tag key themes/entities.

  ## Acceptance Criteria
  - [ ] Prompt template committed in `docs/prompts/summarization.md`.
  - [ ] Batch script writes summaries + tags to SQLite or Parquet.
  - [ ] Process can resume after interruption (idempotent runs).
  - [ ] Evaluation notebook validates summary quality on 10 samples.
  ```
- **Dependencies**: Data Parsing Pipeline
- **Milestone**: `MVP-Data`

## 3. Embedding Store
- **Labels**: `area:data`, `type:feature`, `priority:P1`
- **Description**:
  ```markdown
  ## Goal
  Generate embeddings for each conversation summary and expose semantic search helpers.

  ## Acceptance Criteria
  - [ ] Select `sentence-transformers` model documented with rationale.
  - [ ] Build Faiss/Chroma index with persistence.
  - [ ] Provide function `search_similar(conversation_id, top_k=5)`.
  - [ ] Add smoke test retrieving similar items for three sample conversations.
  ```
- **Dependencies**: Summarization Workflow
- **Milestone**: `MVP-Core`

## 4. UI Skeleton
- **Labels**: `area:ui`, `type:feature`, `priority:P1`
- **Description**:
  ```markdown
  ## Goal
  Stand up Streamlit app with search, filters, results grid, and conversation detail view.

  ## Acceptance Criteria
  - [ ] Homepage lists conversations with summary, tags, timestamp.
  - [ ] Keyword + semantic search integrated.
  - [ ] Filters for date range and tags.
  - [ ] Detail page renders raw conversation with highlight support.
  ```
- **Dependencies**: Embedding Store
- **Milestone**: `MVP-UI`

## 5. Deployment Baseline
- **Labels**: `area:ops`, `type:task`, `priority:P1`
- **Description**:
  ```markdown
  ## Goal
  Containerize vector index + UI, deploy to Raspberry Pi via Docker Compose.

  ## Acceptance Criteria
  - [ ] Dockerfiles for API/UI images.
  - [ ] Compose stack with environment variable management.
  - [ ] Systemd service or cron job ensures stack auto-starts on boot.
  - [ ] Deployment runbook documented in `docs/operations-playbook.md`.
  ```
- **Dependencies**: UI Skeleton, Embedding Store
- **Milestone**: `MVP-Deploy`

## 6. Analytics Dashboards
- **Labels**: `area:ui`, `type:feature`, `priority:P2`
- **Description**:
  ```markdown
  ## Goal
  Visualize conversation volume, tag frequency, and usage trends.

  ## Acceptance Criteria
  - [ ] Generate monthly volume chart with Matplotlib or Altair.
  - [ ] Tag frequency histogram with top 20 tags.
  - [ ] Integrate charts into Streamlit UI (dedicated page or sidebar).
  - [ ] Export static PNGs for documentation.
  ```
- **Dependencies**: Data Parsing Pipeline
- **Milestone**: `MVP-Insights`

## 7. Documentation & Reports
- **Labels**: `type:doc`, `priority:P2`
- **Description**:
  ```markdown
  ## Goal
  Maintain living documentation for setup, architecture, and user workflows.

  ## Acceptance Criteria
  - [ ] Joplin notebook synced with repo docs (export snapshots weekly).
  - [ ] `docs/operations-playbook.md` covers install, troubleshooting, rollback.
  - [ ] Architecture diagram updated in README + docs.
  - [ ] Add `CHANGELOG.md` with release notes.
  ```
- **Dependencies**: Continuous activity
- **Milestone**: `Continuous`

---

### Label Legend
- `area:data` – Ingestion, storage, analytics.
- `area:llm` – Prompting, model integration, inference.
- `area:ui` – Frontend, UX, visualizations.
- `area:ops` – Deployment, automation, observability.
- `type:feature` – Net-new functionality.
- `type:task` – Operational or infrastructure work.
- `type:doc` – Documentation, runbooks, knowledge sharing.
- `priority:P0...P3` – Severity/urgency scale.

### How to Import Quickly
If using GitHub CLI:
```bash
gh issue create --title "Data Parsing Pipeline" --body-file docs/issue-backlog.md --label area:data --label type:feature --label priority:P0
```
Replace the `--body-file` with trimmed sections per issue.
