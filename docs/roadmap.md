# GPTBuddyAI Two-Week MVP Roadmap

This roadmap assumes Day 1 is the kickoff date. Adjust the calendar to match your schedule and add specific dates beside each milestone.

## Days 1–2: Setup & Data Ingestion
- Bootstrap repo, virtual environment, and tooling.
- Unpack OpenAI export, run initial ingestion script.
- Produce baseline metrics: total conversations, date range, average conversation length.
- Stand up GitHub Project board, seed issues, and define labels.

## Days 3–4: Summaries & Tagging
- Install/configure LM Studio model (e.g., `mistral-7b-instruct` GGUF).
- Draft summarization + tagging prompts; test on sample conversations.
- Execute batch run across dataset; capture quality notes in `docs/prompts/`.

## Days 5–6: Embeddings & Vector Index
- Select sentence-transformer model, document rationale.
- Generate embeddings, persist vector index, and expose search helper functions.
- Validate retrieval quality with 5–10 manual queries.

## Days 7–9: UI Skeleton & Visualization
- Implement Streamlit layout: global filters, results table, detail pane.
- Integrate semantic search endpoint and tag/date filters.
- Add charts for monthly chat volume and top tags using Altair/Matplotlib.

## Days 10–11: Deployment & Testing
- Author Dockerfiles, Compose stack, and Pi-specific configuration.
- Deploy to Raspberry Pi; perform smoke tests from LAN devices.
- Measure performance (latency, resource usage) and capture optimizations.

## Days 12–14: Polish & Demo
- Harden error handling, logging, and retry logic across pipelines.
- Refine UI styling, add convenience features (tag clouds, related conversations).
- Prepare demo assets: screenshots, screen capture, release notes.
- Close completed issues, update roadmap for next iteration.

## Stretch Goals (Optional)
- Incorporate spaCy entity extraction for advanced filtering.
- Integrate Qdrant/Weaviate as scalable vector backend.
- Package CLI with Typer for unified command surface.
- Automate backup workflow to S3-compatible storage.

## Tracking Progress
- Update GitHub Project weekly with milestone status.
- Post weekly summary in Joplin notebook and link from `docs/status/` (future).
