# 🎵 Sonus API

**Production-grade cultural song analysis & interpretation engine.**

Powered by Groq LLM, HuggingFace embeddings, Neo4j graph database, and a conversational RAG pipeline for deep musical understanding.

---

## ⚡ Quick Start

### 1. Prerequisites

- **Python 3.12+**
- **Docker** (for Neo4j)
- **FFmpeg** (for audio processing — required for ElevenLabs fallback)

### 2. Start Neo4j

```bash
cd backend
docker compose up -d
```

Wait ~30 seconds for Neo4j to fully start. You can verify at [http://localhost:7474](http://localhost:7474).

> **Default credentials:** `neo4j` / `sonus_password`

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Required keys:
| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key (get one at [console.groq.com](https://console.groq.com)) |
| `ELEVENLABS_API_KEY` | ElevenLabs API key (for transcript fallback) |

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Open API Docs

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | System health check |
| `POST` | `/api/song/ingest` | Ingest a song from YouTube |
| `GET` | `/api/song/{song_id}/transcript` | Get song transcript |
| `POST` | `/api/translate` | Translate song lyrics |
| `GET` | `/api/song/{song_id}/translations` | List all translations |
| `POST` | `/api/rag/ask` | Ask about a song (cultural interpretation) |

---

## 🏗️ Architecture

```
app/
├── api/            # FastAPI route handlers
├── processors/     # Business logic orchestration
├── services/       # External service integrations
├── entities/       # Domain models (dataclasses)
├── schemas/        # Pydantic request/response models
├── database/       # Neo4j driver & Cypher queries
├── config/         # Settings & constants
├── middleware/      # Request logging
└── utils/          # Logger, helpers, exceptions
```

**Data flow:** `API → Processor → Service → External System`

---

## 🗄️ Graph Model (Neo4j)

```
(Artist)-[:CREATED]->(Song)
(Song)-[:HAS_TRANSCRIPT]->(Transcript)
(Song)-[:HAS_TRANSLATION]->(Translation)
(Song)-[:BELONGS_TO_GENRE]->(Genre)
(Song)-[:HAS_CULTURAL_THEME]->(CulturalTheme)
(Session)-[:ASKED]->(Song)
```

---

## 🔧 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Groq API key (required) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `ELEVENLABS_API_KEY` | — | ElevenLabs API key (optional, for fallback) |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `sonus_password` | Neo4j password |
| `NEO4J_DATABASE` | `sonus` | Neo4j database name |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | Chroma persistence directory |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

---

## 📜 License

MIT
