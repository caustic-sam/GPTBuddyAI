# GPTBuddyAI Operations Playbook

Authoritative reference for developers and operators who run GPTBuddyAI locally, in staging, and on the Raspberry Pi deployment target.

## 1. Environments
| Environment | Purpose | Notes |
| --- | --- | --- |
| `local` | Developer workstations (macOS/Linux). | Uses `.env.local`, streams data from local `data/` folder. |
| `pi` | Raspberry Pi production deployment. | Headless Docker Compose stack, persistent volume mounted at `/opt/gptbuddyai`. |
| `ci` | Future GitHub Actions workflows. | Runs tests on pull requests; container specs TBA. |

## 2. Required Tooling
- Python 3.10+
- pip / Poetry (choose one; default pip with `requirements.txt`)
- LM Studio (or alternative local LLM runtime)
- sentence-transformers models (download via `pip` or `huggingface-cli`)
- Docker + Docker Compose v2
- `gh` CLI for GitHub project/issue automation
- Optional: `tmux`, `htop`, `sqlite3`, `faiss-cpu`

## 3. Environment Variables
Create `.env` in repo root (never commit):
```dotenv
DATA_DIR=./data
LM_STUDIO_API=http://127.0.0.1:1234/v1
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_BACKEND=faiss
STREAMLIT_SERVER_PORT=8501
LOG_LEVEL=INFO
```
For Raspberry Pi, store variables in `/opt/gptbuddyai/.env` and reference them in Compose.

## 4. Data Ingestion Workflow
1. Export chat archive from OpenAI (Settings → Data Controls → Export → Download `.zip`).
2. Place archive under `${DATA_DIR}/raw/<timestamp>/`.
3. Run ingestion script (to be implemented):
   ```bash
   python scripts/ingest_conversations.py \
     --input ${DATA_DIR}/raw/2025-01-20/conversations.json \
     --output ${DATA_DIR}/processed/conversations.sqlite
   ```
4. Validate:
   - Execute `sqlite-utils schema ${DATA_DIR}/processed/conversations.sqlite`.
   - Run `pytest tests/ingestion` (future) for smoke tests.

## 5. Summarization & Tagging
- Ensure LM Studio model running with HTTP server enabled.
- Execute summarization job:
  ```bash
  python scripts/run_summarization.py \
    --db ${DATA_DIR}/processed/conversations.sqlite \
    --model-endpoint ${LM_STUDIO_API}
  ```
- Logs stored under `logs/summarization-<date>.log`.
- Resume capability: script should skip rows that already contain summaries.

## 6. Embedding Generation
- Configure backend in `.env` (`faiss` or `chroma`).
- Generate embeddings:
  ```bash
  python scripts/build_embeddings.py --db ${DATA_DIR}/processed/conversations.sqlite
  ```
- Persist indices under `${DATA_DIR}/vector/`.
- Nightly cron (Pi) can refresh embeddings for new rows:
  ```cron
  0 3 * * * /opt/gptbuddyai/.venv/bin/python /opt/gptbuddyai/scripts/build_embeddings.py >> /var/log/gptbuddyai/embeddings.log 2>&1
  ```

## 7. Application Stack
### Streamlit UI
- Launch locally: `streamlit run app/main.py`.
- Exposes environment variables through `.streamlit/secrets.toml` or `.env`.

### API Layer (Optional)
- If building a FastAPI backend, expose endpoints for search, metadata, analytics.
- Document routes in `docs/api.md` (future).

## 8. Deployment (Raspberry Pi)
1. **Prerequisites**
   - Raspberry Pi 4B (8GB RAM recommended), Raspberry Pi OS 64-bit.
   - Docker + Docker Compose installed.
   - External SSD for data storage (mount as `/opt/gptbuddyai`).

2. **Directory Layout**
   ```
   /opt/gptbuddyai/
   ├── .env
   ├── docker-compose.yml
   ├── data/
   ├── logs/
   └── src/ (optional code checkout)
   ```

3. **Deploy**
   ```bash
   cd /opt/gptbuddyai
   docker compose pull
   docker compose up -d
   docker compose logs -f
   ```

4. **Services** (target state)
   - `ui`: Streamlit container (port 8501)
   - `vector`: Faiss/Chroma API (port 8000)
   - `scheduler`: Cron/worker container for nightly jobs

5. **Systemd Service (optional)**
   ```ini
   [Unit]
   Description=GPTBuddyAI Docker Compose stack
   After=network-online.target

   [Service]
   Type=oneshot
   WorkingDirectory=/opt/gptbuddyai
   ExecStart=/usr/bin/docker compose up -d
   ExecStop=/usr/bin/docker compose down
   RemainAfterExit=yes

   [Install]
   WantedBy=multi-user.target
   ```

## 9. Monitoring & Alerting
- **Logs**: Stream to `logs/` directory; optionally forward to Loki/Promtail.
- **Health checks**: Add `/healthz` endpoint (FastAPI) and Streamlit status page.
- **Alerts**: Setup `healthchecks.io` pings for cron jobs; simple email/Slack notifications.

## 10. Backup Strategy
- Weekly snapshot of `${DATA_DIR}` to external drive or S3-compatible storage.
- Use `sqlite-utils dump` to export schema + data before upgrades.
- Store prompt templates and config in Git to maintain history.

## 11. Incident Response
1. Identify service impacted (UI, vector, ingestion).
2. Check container status: `docker compose ps`.
3. Review logs: `docker compose logs <service>`.
4. Roll back to previous image tag if latest deploy fails.
5. Document incident in `docs/incidents/<date>.md`.

## 12. Release Process (Draft)
1. Create release branch `release/v0.x`.
2. Update docs, changelog, and version metadata.
3. Run regression tests locally (unit + UI smoke tests).
4. Tag release: `git tag -a v0.x.y -m "Release notes"`.
5. Push tag to GitHub and publish release notes.

---
Keep this playbook updated alongside infra changes to prevent drift.
