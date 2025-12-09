LoreKeeper

```markdown
# 📚 LoreKeeper

**AI-powered story companion for tracking characters, places, and lore in complex narratives.**

Build a wiki for any novel automatically. Ask questions about your story and get answers with citations. Never lose track of who's who again.

---

## ✨ Features

- **Automatic Entity Extraction** — Detects characters, locations, organizations, and items using NLP
- **AI Story Assistant** — Ask questions about your narrative; get answers with chapter citations
- **Smart Entity Resolution** — Handles duplicates, aliases, and name variations automatically
- **Relationship Tracking** — See how entities connect across chapters
- **Version Control** — Snapshot and restore chapter versions
- **Rich Text Editing** — Full formatting support for writing and editing

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | FastAPI, PostgreSQL, SQLAlchemy, spaCy |
| **AI/RAG** | LangChain, Claude 3.5, Voyage AI embeddings, ChromaDB |
| **Frontend** | React 18, Vite, TanStack Query, TipTap editor |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- [Anthropic API Key](https://console.anthropic.com/settings/keys)
- [Voyage AI API Key](https://dash.voyageai.com/)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/lorekeeper.git
cd lorekeeper

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Frontend setup
cd ../frontend
npm install
```

### Configuration

Create `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/lorekeeper_db
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
VOYAGE_API_KEY=pa-your-key-here
```

### Run

```bash
# Terminal 1 — Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Open **http://localhost:3000**

---

## 📖 Usage

1. **Create a Project** — Add a novel you're writing or reading
2. **Add Chapters** — Paste or write chapter content; entities are extracted automatically
3. **Explore Entities** — Browse detected characters, locations, and items in the sidebar
4. **Ask the AI** — Click the assistant and ask anything about your story
5. **Manage Lore** — Edit entity details, merge duplicates, track relationships

---

## 🔌 API Overview

| Endpoint | Description |
|----------|-------------|
| `GET /api/projects` | List all projects |
| `POST /api/chapters/{project_id}` | Create chapter (triggers NER) |
| `GET /api/entities/{project_id}` | List extracted entities |
| `POST /api/entities/merge` | Merge duplicate entities |
| `POST /api/assistant/{project_id}/ask` | Query AI about story |

Full API docs available at **http://localhost:8000/docs** when running.

---

## ⚙️ Configuration Options

### spaCy Models

```bash
# For better accuracy (larger model)
python -m spacy download en_core_web_lg
```

### Claude Models

In `ai_assistant.py`:

```python
model="claude-3-5-haiku-20241022"   # Fast, cheap
model="claude-3-5-sonnet-20241022"  # Balanced (default)
model="claude-3-opus-20240229"      # Highest quality
```

---

## 📁 Project Structure

```
lorekeeper/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── models.py            # Database models
│   │   ├── routers/             # API endpoints
│   │   └── services/
│   │       ├── ner_service.py   # Entity extraction
│   │       └── ai_assistant.py  # RAG implementation
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── components/
    └── package.json
```

---

## 🗺️ Roadmap

- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Railway)
- [ ] Multi-language support
- [ ] Character relationship graphs
- [ ] Export to PDF/Markdown

