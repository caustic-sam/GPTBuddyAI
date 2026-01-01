# ✅ GPTBuddyAI - Pre-Demo Checklist
## January 1, 2026 - Investor Demo

---

## 🌅 Morning of Demo (2-3 Hours Before)

### **Technical Setup** (30 minutes)

#### **System Check**
- [ ] Laptop charged to 100%
- [ ] macOS updates disabled (Settings → Software Update → Advanced → Uncheck auto-install)
- [ ] Disable notifications (Focus mode ON)
- [ ] Close all apps except Terminal + Browser
- [ ] Clear browser cache / Use fresh incognito window
- [ ] Verify internet connection (if needed for remote demo)

#### **Application Launch**
```bash
# Run these commands in Terminal:

# 1. Navigate to project
cd /Users/jm/myProjects/GPTBuddyAI

# 2. Verify data is intact
ls -lh artifacts/*.parquet artifacts/index/chroma.sqlite3

# 3. Test vector index
python -c "from chromadb import PersistentClient; print(f'Chunks: {PersistentClient(path=\"artifacts/index\").get_collection(\"studykit\").count():,}')"

# Expected output: "Chunks: 60,310"

# 4. Launch Streamlit
streamlit run src/ui/streamlit_app_tabbed.py --server.port 8501

# 5. Open browser
open http://localhost:8501
```

#### **UI Verification** (http://localhost:8501)
- [ ] **Tab 1** (My Conversations) loads without errors
- [ ] Topic cluster image displays
- [ ] Volume chart renders
- [ ] Stats show: "55K+ conversations"

- [ ] **Tab 2** (RAG Query) loads
- [ ] Search box is visible
- [ ] Sample queries display correctly

- [ ] **Tab 3** (NIST Library) loads
- [ ] Metrics show: "337 documents, 32,112 pages, 60,310 chunks"
- [ ] All deltas (+324, +30,568, +32,513) display in green

#### **Query Testing** (Run test script)
```bash
python test_demo_queries.py

# Expected output:
# ✅ PASS on all 5 queries
# ✅ Latency < 1s on all
```

- [ ] All 5 queries pass
- [ ] Latency < 1 second
- [ ] Results look correct

---

## 📸 Screenshots & Materials (1 hour before)

### **Capture Screenshots**
Use Command+Shift+4 (Mac) to capture these:

- [ ] **Tab 1 - Topic Map**
  - Full screen showing visualization
  - Stats visible at top
  - Filename: `demo_tab1_topics.png`

- [ ] **Tab 2 - Query 1 Results**
  - Query text visible
  - Answer displayed
  - Citations expanded
  - Filename: `demo_query1_personal.png`

- [ ] **Tab 2 - Query 2 Results**
  - NIST SP 800-63 citations
  - Filename: `demo_query2_nist.png`

- [ ] **Tab 2 - Query 4 Results**
  - Cross-corpus query (the wow moment)
  - Filename: `demo_query4_crosscorpus.png`

- [ ] **Tab 3 - NIST Library**
  - Stats with deltas
  - Filename: `demo_tab3_nist.png`

### **Slide Deck Final Check**
- [ ] All 12 slides complete
- [ ] Screenshots embedded
- [ ] Fonts render correctly
- [ ] Animations disabled (if using PowerPoint/Keynote)
- [ ] Export as PDF backup
- [ ] Copy to USB drive (backup)

### **Demo Materials**
- [ ] Laptop
- [ ] HDMI/USB-C adapter
- [ ] Backup phone (with hotspot)
- [ ] USB drive with PDF deck
- [ ] Water bottle
- [ ] Business cards (if applicable)
- [ ] Notepad + pen

---

## 🎤 Pre-Demo Rehearsal (30 minutes before)

### **Run Through Demo**
- [ ] Practice opening (15 seconds)
- [ ] Navigate to Tab 1, pause, explain (30 seconds)
- [ ] Run Query 1, narrate while searching (45 seconds)
- [ ] Run Query 2, show NIST depth (45 seconds)
- [ ] Run Query 4, the wow moment (60 seconds)
- [ ] Closing pitch (30 seconds)

**Total Time**: ~3-4 minutes (leave buffer for questions)

### **Narration Practice**
Practice these key lines out loud:

**Opening**:
> "I want to show you something I built in 10 days. GPTBuddyAI analyzed 55,000 of my conversations and 337 NIST compliance documents. Everything runs locally on this laptop."

**Tab 1 Transition**:
> "The AI discovered 25 distinct topics in my thinking without me tagging anything. Here's my 2-year intellectual journey visualized."

**Query 1 (while it searches)**:
> "Watch this. I'm asking it to summarize themes from 2 years of conversations. The system is searching 60,000 passages..."

**Query 4 (the climax)**:
> "This is the breakthrough. It's comparing my personal philosophy with official NIST standards and showing me where they align—and where they don't."

**Closing**:
> "What you just saw: instant expert answers, perfect citations, zero privacy risk. Imagine this for your organization's institutional knowledge."

---

## 🎯 Demo Environment Setup (At Venue)

### **Room Setup** (15 minutes before)
- [ ] Test display connection (HDMI/AirPlay)
- [ ] Verify screen resolution (1920x1080 or higher)
- [ ] Adjust room lighting (screen visible, not too dark)
- [ ] Check WiFi signal (if needed)
- [ ] Test audio (if doing remote demo)
- [ ] Position yourself for audience sightline

### **Browser Setup**
- [ ] Zoom to 125-150% (⌘+ on Mac)
- [ ] Full screen mode (Command+Shift+F)
- [ ] Pin tab (right-click tab → Pin)
- [ ] Disable browser extensions (use Incognito)

### **Backup Plans**
- [ ] Screenshots in slides (if UI fails)
- [ ] PDF deck on phone (if laptop dies)
- [ ] Printed one-pager (if all tech fails)
- [ ] Rehearsed verbal-only pitch (if projector fails)

---

## ⚠️ Troubleshooting - Quick Fixes

### **If Streamlit Won't Start**
```bash
# Kill existing processes
pkill -f streamlit

# Restart
streamlit run src/ui/streamlit_app_tabbed.py --server.port 8501
```

### **If Query is Slow (>5s)**
- **Cause**: Model loading first time
- **Fix**: Run Query 2 once before demo to warm up
- **Explain**: "The AI is loading... first query takes a moment"

### **If Wrong Results**
- **Pivot**: "Let me try a different query" → Use backup query
- **Or**: Switch to Tab 1 topic map → Always works

### **If UI Crashes**
- **Immediately**: Show screenshots in slides
- **Say**: "Let me show you what it looks like..." → Continue with slides
- **Recovery**: Restart Streamlit during Q&A

---

## 📊 Success Metrics - Track These

### **Investor Reactions to Note**
- [ ] Leaned forward during demo?
- [ ] Took notes during queries?
- [ ] Asked "How did you do that?" or "Can I try?"
- [ ] Pulled out phone to take photo of screen?
- [ ] Asked about pricing/timeline unprompted?

### **Questions to Expect**
**Technical**:
- "How accurate is it?" → **A**: "Retrieval is deterministic, LLM quality depends on model"
- "Can it scale?" → **A**: "Yes, vector DBs scale to millions of docs"
- "What about cost?" → **A**: "Zero ongoing—runs locally, no API fees"

**Business**:
- "Who's your target customer?" → **A**: "Privacy-conscious enterprises: finance, healthcare, legal"
- "What's your moat?" → **A**: "Local-first privacy + NIST compliance expertise"
- "How long to build?" → **A**: "10 days for MVP, modular to extend"

**Objections**:
- "Why not just use ChatGPT?" → **A**: "Privacy. Their data leaves their device, plus they need compliance guarantees"
- "This is just RAG..." → **A**: "Yes, but RAG + privacy + compliance + 10-day execution is the value"

---

## 🎉 Post-Demo (Immediately After)

### **While They're Excited**
- [ ] Get email addresses
- [ ] Ask: "What resonated most?"
- [ ] Gauge interest (1-10 scale, internal note)
- [ ] Schedule follow-up within 48 hours

### **Send Within 1 Hour**
- [ ] Thank you email
- [ ] PDF deck attached
- [ ] Link to GitHub (if comfortable)
- [ ] "Happy to answer any questions"

### **Follow-Up Within 24 Hours**
- [ ] Personalized email addressing their specific questions
- [ ] Share key metrics (60K chunks, 337 docs, <1s latency)
- [ ] Offer custom demo with their data (if appropriate)

---

## ✅ Final Checklist - Read Aloud Before Demo

**Technical**:
- [ ] UI running at http://localhost:8501
- [ ] All 3 tabs load correctly
- [ ] Test query completed successfully
- [ ] Laptop at 100% battery
- [ ] Notifications disabled

**Materials**:
- [ ] Slide deck ready
- [ ] Screenshots captured
- [ ] Backup PDF on USB
- [ ] Water nearby

**Mental**:
- [ ] Deep breath, smile
- [ ] You know this inside-out
- [ ] 10 days of work → 3 minutes of wow
- [ ] They're going to love it

---

## 🚀 You've Got This!

**Remember**:
- ✅ You built a working MVP in 10 days
- ✅ The tech works (tested 5 queries, all <1s)
- ✅ The story is compelling (privacy + compliance + speed)
- ✅ You know more about this than anyone in the room

**Final Thought**:
> "This isn't just a demo. It's proof that local-first AI is not only possible—it's better."

---

**Go crush it! 🎉**

_Last updated: December 31, 2025_
_Demo: January 1, 2026_
