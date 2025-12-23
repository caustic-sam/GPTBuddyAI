# GPTBuddyAI - 2026 MVP Sprint Roadmap

**Timeline**: Dec 21, 2025 → Jan 1, 2026 (10 days)
**Demo Date**: January 1, 2026 (in-person, live demo + slides)
**Team**: Solo developer
**Focus**: Aesthetics-first + functional RAG pipeline

---

## Success Criteria

### Must-Have for Investor Demo
1. **Live RAG Query** with citations on real OpenAI + NIST data
2. **Beautiful Analytics Dashboard** (conversation volume, tag frequency)
3. **Nordic-Themed UI** (sleek greys/blues, minimalist design)
4. **rpi-cortex Deployment** with Docker + backup automation
5. **Presentation Slides** showcasing privacy-first value proposition

---

## Phase Breakdown

### Phase 1: Foundation (Dec 21-22) - Days 1-2
**Milestone**: Working data pipeline

- [x] Environment setup (Python, venv, .env, directories)
- [x] GitHub Project board + 8 issues created
- [ ] Ingest OpenAI export → `artifacts/openai.parquet`
- [ ] Ingest NIST PDFs → `artifacts/docs.parquet`
- [ ] Generate baseline metrics
- [ ] Design Nordic UI color palette

**Deliverables**:
- Parquet datasets with metadata
- Baseline analytics (conversation count, date range)
- UI design mockup

---

### Phase 2: Core RAG + UI Polish (Dec 23-26) - Days 3-6
**Milestone**: Beautiful, functional UI with working RAG

#### Dec 23
- [ ] Build ChromaDB vector index
- [ ] Implement query.py with citations
- [ ] Wire Streamlit UI to RAG backend
- [ ] Apply Nordic theme CSS

#### Dec 24
- [ ] Analytics dashboard implementation
  - Conversation volume over time (line chart)
  - Tag frequency histogram
  - Date range filters
- [ ] Integrate charts into main page

#### Dec 25
- [ ] UI polish and branding
  - Finalize color scheme
  - Typography improvements
  - Smooth transitions/hover effects
  - Logo integration (or placeholder)

#### Dec 26
- [ ] Testing + refinement
  - Write pytest tests (ingestion, RAG)
  - Fix bugs
  - Performance profiling

**Deliverables**:
- Polished Streamlit UI with Nordic design
- Working RAG Q&A with citations
- Analytics dashboards
- Test coverage for core components

---

### Phase 3: Deployment + Automation (Dec 27-29) - Days 7-9
**Milestone**: Production deployment on rpi-cortex

#### Dec 27
- [ ] Write Dockerfile for Streamlit
- [ ] Create docker-compose.yml
- [ ] Test locally on Mac

#### Dec 28
- [ ] Deploy to rpi-cortex
- [ ] Configure systemd auto-start
- [ ] Smoke test from LAN devices
- [ ] Optional: Cloudflare Tunnel setup

#### Dec 29
- [ ] Backup/restore automation
  - Backup script (vector index + parquet)
  - Test restore procedure
  - Cron job for nightly backups
- [ ] Document disaster recovery

**Deliverables**:
- Dockerized application
- Running on rpi-cortex
- Automated backup system
- Updated operations playbook

---

### Phase 4: Demo Prep (Dec 30-31) - Days 10-11
**Milestone**: Demo-ready presentation

#### Dec 30
- [ ] Create investor slide deck (10-15 slides)
  - Problem: Privacy concerns with cloud AI
  - Solution: Local-first RAG analytics
  - Demo: Live walkthrough screenshots
  - Architecture diagram
  - Roadmap: Phase 2 features
- [ ] Rehearse demo (3-5 minutes)
- [ ] Prepare 3-5 impressive sample queries

#### Dec 31
- [ ] Final polish and bug fixes
- [ ] Optimize demo queries
- [ ] Update README with screenshots
- [ ] Create Confluence project overview
- [ ] Buffer for unexpected issues

**Deliverables**:
- Polished slide deck
- Rehearsed demo flow
- Updated documentation
- Confluence/Jira integration established

---

## Jan 1, 2026: DEMO DAY

### Pre-Demo Checklist
- [ ] rpi-cortex running and accessible
- [ ] Streamlit UI loads in <3 seconds
- [ ] Sample queries return accurate citations
- [ ] Analytics charts display correctly
- [ ] Backup verified
- [ ] Laptop charged, display mirroring tested
- [ ] Slide deck loaded and ready

---

## Priority Matrix

### Priority 1 (Critical - Must Have)
- End-to-end RAG pipeline (ingest → embed → query → cite)
- Analytics dashboards (conversation volume, tag frequency)
- Raspberry Pi deployment with Docker
- Backup/restore automation

### Priority 2 (High - Important for Polish)
- Nordic-themed Streamlit UI
- Custom branding (logo, colors)
- Test coverage (pytest)
- Confluence/Jira integration

### Priority 3 (Medium - Nice to Have)
- Multi-corpus support (OpenAI + NIST working, IAPP phase 2)
- Citation display with provenance tracking
- Study guide generation
- Monitoring/observability

### Priority 5 (Low - Deferred)
- LoRA fine-tuning
- Core ML export
- Performance optimization
- PDF export capabilities

---

## Parallel Workstream Strategy

Since working solo, time-slicing by phase:

- **Days 1-3**: Stream A+B (Data Pipeline + RAG Engine)
- **Days 3-6**: Stream C (UI/UX)
- **Days 7-9**: Stream D+E (Infrastructure + Quality)
- **Days 10-11**: Demo Prep

---

## Key Decisions

1. **Python 3.10** (venv) - stable, compatible with all deps
2. **Streamlit** as primary UI framework
3. **ChromaDB** for vector storage
4. **MLX-LM** for local inference (Apple Silicon optimized)
5. **Docker Compose** for rpi-cortex deployment
6. **Nordic Design**: Greys (#F5F5F5, #E0E0E0), Blues (#4A90E2, #2E5C8A)
7. **IAPP corpus** deferred to Phase 2 (post-demo)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data ingestion fails | Validated code exists, real data available |
| UI doesn't look polished | Nordic design system pre-defined, CSS ready |
| rpi-cortex deployment issues | Test locally first, buffer day for fixes |
| Demo hardware failure | Backup on MacBook Pro, slides have screenshots |
| Time overrun | Priority matrix ensures P1 features complete first |

---

## Success Metrics

- **Technical**: RAG queries return relevant results with <2s latency
- **Visual**: UI achieves "wow" factor (Nordic minimalist aesthetic)
- **Operational**: System runs on rpi-cortex for 72+ hours without restart
- **Business**: Investor feedback positive, interest in Phase 2 funding

---

_Created: Dec 21, 2025_
_Last Updated: Dec 21, 2025_
_Owner: JM + Claude Sonnet 4.5_
