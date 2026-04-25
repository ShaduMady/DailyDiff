# DailyDiff
### A personal growth changelog powered by local AI

> Type a messy paragraph about your day.  
> Get back a structured, versioned entry — with key ideas, open questions, action items, and a drift score.  
> Runs entirely on your machine. Free forever.

---

## The Problem

Most people take notes. Almost nobody structures them.

DailyDiff takes your raw brain dump — whatever happened today, no formatting needed — and turns it into a clean changelog entry using a locally-running AI model. Over time, you build a versioned log of your own thinking, with patterns and connections surfaced automatically.

*Ship yourself. One version at a time.*

---

## Core Features

- **Note structuring** — paste messy text, get back a clean entry with summary, changelog, key ideas, open questions, and action items
- **Versioned entries** — every day is a version (`v0.0.1`, `v0.0.2`...) so you can see yourself improving over time
- **Drift score** — set a weekly focus, and every entry is scored on how aligned you are with it
- **Connection finder** — the AI compares your new entry to the last 7 and surfaces links between your thoughts
- **Task extraction** — action items auto-populate a task list, grouped by version, filterable by Open / Done / All
- **Streaks** — track consistency per tag (`learning`, `building`, `social`, `health`, `blocked`, `thinking`)
- **Weekly summary** — one click generates a release note for the week: highlights, blockers, and a pattern insight
- **Real-time streaming** — watch the AI think as it processes your notes, token by token

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python, FastAPI, SQLite, SQLAlchemy |
| AI | Ollama — llama3.2, runs fully locally |
| Frontend | React (single file, no build step) |

**Why local AI?** Your daily reflections are personal. They shouldn't leave your machine. Ollama runs the model entirely on your hardware — no API keys, no usage fees, no data sent anywhere.

---

## Setup

```bash
# 1. Install Ollama and pull the model
# → Download from https://ollama.com/download
ollama pull llama3.2

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
# source venv/bin/activate        # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn backend.main:app --reload

# 5. Open the app
# → http://localhost:8000
```

No `.env` file. No API keys. No configuration.

---

## User Workflow

```
Capture  →  Structure  →  Reflect  →  Act
   |             |            |         |
 Type raw      Local AI    Drift      Tasks
  notes        parses      score +    auto-
              entry        connections extracted
                    ↓
        builds your knowledge graph over time
```

---

## How I Used AI to Build This

This wasn't just built *with* AI as a feature — AI was my primary building tool throughout.

- **Claude Code** — used to scaffold the FastAPI backend, SQLite schema, and React frontend from scratch
- **Prompt engineering** — iterated on the structuring prompt to get consistent JSON output, especially for drift scoring and connection finding
- **Context design** — the key insight was passing the last 7 entries + weekly focus into every AI call, which dramatically improved the quality of connections and drift scores
- **Local-first pivot** — switched from a paid cloud AI API to Ollama mid-build, making the product free and private without sacrificing quality

---

## What I Deliberately Left Out

- No user auth — single user, runs locally
- No mobile app — web only for now
- No rich text editor — plain textarea is intentional friction

These are scope decisions. The core loop had to work first.

---

## Roadmap

### Phase 1 — Built
- [x] AI-powered note structuring with drift score + connection finder
- [x] Versioned entry log
- [x] Task extraction and management
- [x] Streak tracking per tag
- [x] Weekly summary generation
- [x] Real-time streaming responses
- [x] 100% local — no API keys, no cloud, no cost

### Phase 2 — Next
- [ ] Mobile app (iOS + Android) — capture on the go
- [ ] Voice memo input → auto-transcribe → structure
- [ ] Browser extension — clip tabs and articles directly into DailyDiff
- [ ] AI reflection chat — *"what have I been avoiding this week?"*

### Phase 3 — Public Product
- [ ] User accounts + cloud sync (opt-in)
- [ ] Team mode — shared logs, async standups
- [ ] Weekly email digest every Sunday
- [ ] Integrations API (Linear, Slack, Obsidian)

---

## Future Vision

DailyDiff started as a personal tool but the problem it solves is universal — people capture a lot, structure almost nothing, and lose most of what they learn.

The long-term vision is a thinking partner that lives across your devices: capturing on mobile, surfacing connections in the browser, and giving you a weekly honest reflection on where your time and attention actually went — versus where you said they'd go.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/entry` | Submit notes, receive structured entry |
| `POST` | `/entry/stream` | Same, with real-time token streaming |
| `GET` | `/entries` | All entries, newest first |
| `POST` | `/todos` | Create a task |
| `GET` | `/todos` | All tasks |
| `PATCH` | `/todos/{id}` | Toggle task complete / incomplete |
| `GET` | `/weekly-summary` | AI-generated weekly release note |
| `PUT` | `/settings/weekly-focus` | Set weekly focus |
| `GET` | `/settings/weekly-focus` | Get current weekly focus |

---

## Project Structure

```
DailyDiff/
├── backend/
│   ├── main.py               # App entry point, middleware, routing
│   ├── database.py           # Models + seeding
│   ├── models.py             # Pydantic schemas
│   ├── routes/
│   │   ├── entries.py        # Entry creation + retrieval
│   │   ├── todos.py          # Task management
│   │   └── weekly.py         # Weekly summary + focus settings
│   └── services/
│       └── agent.py          # AI prompts + Ollama integration
├── frontend/
│   └── index.html            # React app (single file, no build step)
└── requirements.txt
```

---

*Built in a day. Used every day.*
