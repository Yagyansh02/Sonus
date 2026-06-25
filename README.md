<div align="center">

# 🎵 Sonus

### Cultural Song Analysis & Interpretation Engine

**Decode the soul, slang, and emotional weight of any song — powered by AI.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=flat-square)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## What is Sonus?

Sonus is a full-stack AI system that ingests any song from YouTube and makes it deeply understandable — not just translated, but *culturally interpreted*.

It acts as an **elite ethnomusicologist**: decoding slang, metaphors, socio-political commentary, double-entendres, and emotional weight behind lyrics through a conversational RAG (Retrieval-Augmented Generation) pipeline.

### What makes it different

| Feature | Description |
|---------|-------------|
| 🧠 **Cultural RAG** | Ask anything about a song — the AI responds like a music scholar, not a dictionary |
| 🎙️ **Dual-Source Transcripts** | YouTube captions → automatic ElevenLabs STT fallback |
| 🌍 **Literary Translation** | Lyrics are *localized*, not translated — preserving poetic meaning and rhythm |
| 🕸️ **Knowledge Graph** | Song, artist, genre, theme, and session relationships stored in Neo4j |
| 💾 **Persistent Vectors** | Per-song ChromaDB collections — no re-embedding on restart |
| 🤖 **Groq-Only LLM** | Ultra-fast Llama 3.3 70B inference for all AI tasks |

---

## Table of Contents

- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Backend Deep Dive](#backend-deep-dive)
- [Frontend](#frontend)
- [Graph Database Model](#graph-database-model)
- [API Reference](#api-reference)
- [Setup & Running](#setup--running)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)

---

## Project Structure

```
Sonus/
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app factory + lifespan
│   │   ├── api/               # Route handlers (thin HTTP layer)
│   │   │   ├── health.py      # GET  /api/health
│   │   │   ├── songs.py       # POST /api/song/ingest
│   │   │   ├── transcript.py  # GET  /api/song/{id}/transcript
│   │   │   ├── translation.py # POST /api/translate
│   │   │   └── rag.py         # POST /api/rag/ask
│   │   ├── processors/        # Business logic orchestration
│   │   │   ├── song_processor.py
│   │   │   ├── transcript_processor.py
│   │   │   ├── translation_processor.py
│   │   │   └── rag_processor.py
│   │   ├── services/          # Single-responsibility external integrations
│   │   │   ├── groq_service.py
│   │   │   ├── youtube_service.py
│   │   │   ├── transcript_service.py
│   │   │   ├── vector_service.py
│   │   │   ├── elevenlabs_service.py
│   │   │   ├── translation_service.py
│   │   │   └── neo4j_service.py
│   │   ├── entities/          # Domain models (dataclasses)
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── database/          # Neo4j driver + Cypher queries
│   │   ├── config/            # Settings + prompt templates
│   │   ├── middleware/        # Request logging
│   │   └── utils/             # Logger, helpers, exceptions
│   ├── tests/                 # Pytest test suite
│   ├── docker-compose.yml     # Neo4j Docker setup
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                  # Next.js 16 frontend
│   └── src/app/
│       └── page.tsx           # API tester UI
│
└── README.md                  # This file
```

---

## Technology Stack

### Backend

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **API Framework** | FastAPI | ≥0.115 | Async REST API, auto-generated Swagger UI |
| **LLM** | Groq (Llama 3.3 70B) | — | Cultural interpretation, translation, metadata |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` | — | Semantic lyric embeddings |
| **Vector Store** | ChromaDB | ≥1.5 | Per-song persistent vector collections |
| **Graph DB** | Neo4j | ≥5.28 | Song/artist/genre/theme knowledge graph |
| **RAG Framework** | LangChain + LangChain-Classic | ≥1.3 | Retrieval chains, history-aware retriever |
| **Transcript (Primary)** | LangChain YoutubeLoader | — | YouTube caption extraction |
| **Transcript (Fallback)** | ElevenLabs Scribe v2 | ≥2.3 | Speech-to-text from audio |
| **Audio Download** | yt-dlp | ≥2026.3 | YouTube audio extraction for STT |
| **Validation** | Pydantic v2 | ≥2.10 | Request/response models, settings |
| **Server** | Uvicorn | ≥0.34 | ASGI server |
| **Runtime** | Python | 3.12+ | — |

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 16.2.9 | React framework with App Router |
| React | 19.2.4 | UI library |
| TypeScript | ^5 | Type safety |
| Tailwind CSS | ^4 | Utility-first styling |

---

## Architecture

### High-Level Data Flow

```
HTTP Request
     │
     ▼
┌──────────────────┐
│   API Layer      │  ← Validates input, routes to processor
│  (app/api/)      │    Returns typed Pydantic responses
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Processor Layer  │  ← Orchestrates multi-step business logic
│ (app/processors/)│    Knows "what to do and when"
└────────┬─────────┘
         │
     ┌───┴────────────────────────┐
     ▼                            ▼
┌──────────────┐        ┌──────────────────┐
│ Service Layer│        │  Service Layer   │
│  (Groq LLM) │        │  (YouTube, STT,  │
│              │        │   ChromaDB,      │
└──────────────┘        │   Neo4j, etc.)   │
                        └──────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
     │    Neo4j     │  │   ChromaDB   │  │  External    │
     │  (Graph DB)  │  │  (Vectors)   │  │  APIs        │
     └──────────────┘  └──────────────┘  └──────────────┘
```

### Architectural Principles

- **Separation of concerns** — each layer has a single, well-defined job
- **API layer is thin** — just validates, delegates, serializes
- **Processor layer orchestrates** — coordinates multiple services for a workflow
- **Service layer is atomic** — one service = one external system/capability
- **All config is environment-driven** — zero hardcoded secrets

---

## Backend Deep Dive

### Layer 1 — Config (`app/config/`)

#### `settings.py`
Uses **Pydantic BaseSettings** to load all configuration from environment variables with full type validation. A `@lru_cache` singleton ensures the settings object is parsed once at startup and reused everywhere.

#### `constants.py` — Prompt Engineering Hub
All LLM prompt templates live here, separate from service logic so they can be tuned without touching business code:

- **Contextualize Prompt** — Reformulates follow-up questions into self-contained queries by resolving pronouns and references from chat history (e.g., "what does *it* mean?" → "what does the second verse of Song X mean?")
- **Ethnomusicologist Prompt** — Core AI persona. Instructs the LLM to decode metaphors, slang, cultural idioms, socio-political commentary, and emotional weight — never literal translation
- **Translation Prompt** — Literary localization philosophy: the output should feel *natively written* in the target language, not mechanically translated
- **Metadata Extraction Prompt** — Asks the LLM to classify genres, cultural themes, language, mood, and musical era from lyrics in structured JSON

Chunking configuration: `CHUNK_SIZE=400`, `CHUNK_OVERLAP=60`, lyric-aware separators (`\n\n`, `\n`, `♪`, `. `, `, `, ` `).

---

### Layer 2 — Utils (`app/utils/`)

#### `logger.py`
Structured `key=value` log format, configurable level, `sonus.*` namespace hierarchy. Silences noisy third-party loggers (chromadb, httpx, neo4j).

#### `helpers.py`
- `generate_id()` — UUID4 hex for entity IDs
- `extract_video_id(url)` — YouTube URL parser (standard, short `youtu.be`, embed, music URLs)
- `sanitize_collection_name(name)` — Ensures Chroma collection name compliance
- `truncate_text(text, max)` — Safe truncation with ellipsis

#### `exceptions.py`
Full custom exception hierarchy. Every exception carries a machine-readable `error_code` and HTTP `status_code`:

```
SonusException (base, 500)
├── SongNotFoundError          (404)
├── TranscriptNotFoundError    (404)
├── SessionNotFoundError       (404)
├── TranslationError           (500)
├── VectorStoreError           (500)
├── RAGProcessingError         (500)
├── InvalidYouTubeURLError     (400)
└── ExternalServiceError       (502)
    ├── YouTubeExtractionError
    ├── ElevenLabsError
    └── Neo4jConnectionError
```

A global `sonus_exception_handler` registered in `main.py` catches any `SonusException` and converts it to a consistent JSON error response automatically.

---

### Layer 3 — Entities (`app/entities/`)

Pure Python dataclasses — no business logic, just data containers with `to_dict()` serialization.

| Entity | Key Fields | Purpose |
|--------|-----------|---------|
| `Song` | song_id, title, artist, youtube_url, thumbnail, language, genres, cultural_themes, mood, era | Primary domain entity |
| `Transcript` | transcript_id, song_id, content, source | Lyrics with provenance (`youtube` / `elevenlabs`) |
| `Translation` | translation_id, song_id, target_language, translated_lyrics, notes, confidence_score | Localized lyrics |
| `Session` | session_id, created_at | RAG conversation session |
| `UserQuery` | query_id, session_id, song_id, question, answer, sources | Single Q&A exchange |

---

### Layer 4 — Schemas (`app/schemas/`)

**Pydantic v2 models** enforcing API contracts with validation and auto-generated OpenAPI docs.

**Request schemas:**
- `SongIngestRequest` — validates YouTube URL format with `HttpUrl`
- `TranslateRequest` — accepts `song_id` or `youtube_url` + `target_language`
- `RAGAskRequest` — validates `song_id`, `session_id`, `question` (1–2000 chars)

**Response schemas:**
- `SongIngestResponse` — full song data including genres and cultural themes
- `TranscriptResponse` — content with source provenance
- `TranslationResponse` — translated lyrics, translator notes, confidence score
- `RAGAskResponse` — answer text + retrieved source lyric chunks
- `HealthResponse` — per-service health status
- `ErrorResponse` — consistent `{detail, error_code}` shape

---

### Layer 5 — Database (`app/database/`)

#### `neo4j.py` — Driver Lifecycle
Manages a singleton `AsyncDriver` using FastAPI's lifespan context manager:
- **Startup:** Creates driver, calls `verify_connectivity()` against the `sonus` database
- **Shutdown:** Gracefully closes the driver
- **Dependency:** `get_neo4j_session()` yields a per-request `AsyncSession`

#### `queries.py` — Cypher Constants
All graph queries are string constants — never scattered across business code. Includes constraints for all 7 node types (Song, Artist, Genre, CulturalTheme, Transcript, Translation, Session) and all CRUD operations.

---

### Layer 6 — Services (`app/services/`)

Each service has a **single responsibility**.

#### `groq_service.py`
Factory: `get_llm(temperature)` → `ChatGroq`. Centralizes model name and API key sourcing so all LLM consumers are one config change away from switching models.

#### `youtube_service.py`
- `fetch_video_metadata(url)` — yt-dlp title/artist/thumbnail extraction with graceful fallback
- `download_audio(url)` — Downloads audio as MP3 via yt-dlp + FFmpeg post-processing to a temp directory. Returns `Path` for ElevenLabs ingestion.

#### `transcript_service.py`
Wraps LangChain's `YoutubeLoader` to fetch captions/subtitles. Supports 9 languages. Returns `None` when unavailable — the processor handles the fallback decision.

#### `vector_service.py`
Manages persistent ChromaDB collections with HuggingFace embeddings:
- **Singleton embeddings model** — initialized once, reused across all requests
- **Per-song isolation** — collection named `song_{song_id}`, preventing cross-contamination
- **Smart load-or-create** — loads existing collection if it has data; creates new otherwise
- `create_or_load_index(song_id, documents)` — main entry point
- `get_retriever(song_id, k=4)` — returns a LangChain `VectorStoreRetriever`

#### `elevenlabs_service.py`
Sends MP3 files to the **ElevenLabs Scribe v2** API for speech-to-text transcription. Validates the API key is configured before attempting the call. Used exclusively when YouTube captions are unavailable.

#### `translation_service.py`
Uses the Groq LLM with the literary localization prompt to translate lyrics. Returns structured JSON with `translated_lyrics`, `translation_notes`, and `confidence_score`. Handles markdown code-fence stripping from LLM responses.

#### `neo4j_service.py`
Async wrapper around all Cypher operations:
- `create_song()` — Song node + Artist, Genre, CulturalTheme relationships in one call
- `get_song()` / `get_song_by_url()` — Fetch with all related nodes joined
- `create_transcript()` / `get_transcript()`
- `create_translation()` / `get_translations()`
- `create_or_get_session()` / `link_session_to_song()`
- `setup_constraints()` — Idempotent, called at startup

---

### Layer 7 — Processors (`app/processors/`)

Processors **orchestrate** multiple services into complete business workflows.

#### `transcript_processor.py` — The Fallback Pipeline

```
Step 1 → Try YoutubeLoader (captions/subtitles)
           ↓ SUCCESS: return (content, "youtube")
           ↓ FAIL:
Step 2 → Download audio via yt-dlp
Step 3 → Transcribe via ElevenLabs Scribe v2
Step 4 → Clean up temp audio files
           ↓
         return (content, "elevenlabs")
```

If both fail, raises `TranscriptNotFoundError`. This automatic fallback is transparent to all callers.

#### `song_processor.py` — Full Ingestion Pipeline

```
1. Check Neo4j if song already ingested by URL → return early if yes
2. Fetch YouTube metadata (title, artist, thumbnail)
3. Retrieve transcript (YouTube → ElevenLabs fallback)
4. Extract genre, cultural_themes, language, mood, era via Groq LLM
5. Create persistent ChromaDB vector index for the song
6. Write Song + Transcript nodes + all relationships to Neo4j
7. Return Song entity
```

The LLM metadata extraction (step 4) is unique — it reads the lyrics and auto-classifies the song with zero human input.

#### `translation_processor.py`

```
1. Verify song exists in Neo4j
2. Retrieve stored transcript
3. Call translation_service → literary localization
4. Store Translation node → (Song)-[:HAS_TRANSLATION]->(Translation)
5. Return Translation entity
```

#### `rag_processor.py` — Conversational RAG

The heart of Sonus. Migrated and greatly enhanced from the original CLI prototype.

```
1. Verify song exists in Neo4j
2. Get or build RAG chain (cached per song_id):
   ├── Load persistent vector retriever for this song
   ├── Build history-aware retriever (resolves follow-up references)
   └── Wrap with Ethnomusicologist answer chain + message history
3. Link session → song in Neo4j
4. Invoke chain: {question, chat_history} → {answer, context_chunks}
5. Return {answer, sources, session_id, song_id}
```

Key design decisions:
- **Chain caching per `song_id`** — expensive to build, reused across requests
- **Session isolation** — history keyed by `"{session_id}:{song_id}"` — different songs don't share history
- **In-memory history** — `ChatMessageHistory` per session key (stateful within server lifetime)

---

### Layer 8 — API (`app/api/`)

Thin FastAPI route handlers. Their only jobs: validate input, call a processor, serialize output.

| File | Endpoints |
|------|-----------|
| `health.py` | `GET /api/health` |
| `songs.py` | `POST /api/song/ingest` |
| `transcript.py` | `GET /api/song/{song_id}/transcript` |
| `translation.py` | `POST /api/translate`, `GET /api/song/{song_id}/translations` |
| `rag.py` | `POST /api/rag/ask` |

All endpoints include Pydantic response types, error response schemas, and OpenAPI descriptions.

---

### Application Entry Point (`app/main.py`)

```python
# Lifespan:  setup logging → init Neo4j → run constraints → yield → close Neo4j
# Middleware: CORS + RequestLoggerMiddleware (logs method, path, status, ms)
# Exceptions: SonusException → consistent JSON handler
# Routers:   all 5 route modules mounted under /api
```

---

## Frontend

The frontend (`frontend/`) is a **Next.js 16** application built with React 19 and Tailwind CSS 4.

### Purpose

It serves as an **interactive API tester UI** — a developer-facing interface for testing every backend endpoint without needing Postman or curl.

### Features

- **Tab-based navigation** — switch between Health, Ingest Song, RAG Ask, Transcript, and Translate sections
- **Live form inputs** — enter YouTube URLs, song IDs, questions, and target languages
- **Real-time JSON output** — responses displayed in a monospace code terminal with syntax highlighting
- **Status codes visible** — HTTP status shown alongside each response
- **Loading states** — animated pulse indicator during requests

### Tech Decisions

- Next.js App Router (`src/app/page.tsx` as a single client component)
- Tailwind CSS 4 with PostCSS
- TypeScript throughout
- Talks to `http://localhost:8000/api` (configurable via `baseUrl` constant)

### Running the Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

---

## Graph Database Model

Sonus models musical knowledge as a property graph in Neo4j.

### Nodes

| Label | Properties | Description |
|-------|-----------|-------------|
| `Song` | song_id, title, youtube_url, thumbnail, language, mood, era, created_at | Primary entity |
| `Artist` | name | Song creator |
| `Genre` | name | Music genre (e.g. Hip-Hop, Bollywood Pop, K-Pop) |
| `CulturalTheme` | name | Thematic tag (e.g. Heartbreak, Social Justice, Devotion) |
| `Transcript` | transcript_id, content, source, created_at | Lyrics text |
| `Translation` | translation_id, target_language, translated_lyrics, notes, confidence_score, created_at | Localized lyrics |
| `Session` | session_id, created_at | Conversation session |

### Relationships

```cypher
(Artist)-[:CREATED]->(Song)
(Song)-[:BELONGS_TO_GENRE]->(Genre)
(Song)-[:HAS_CULTURAL_THEME]->(CulturalTheme)
(Song)-[:HAS_TRANSCRIPT]->(Transcript)
(Song)-[:HAS_TRANSLATION]->(Translation)
(Session)-[:ASKED]->(Song)
```

### Example Graph Queries

```cypher
// Find all songs by genre
MATCH (s:Song)-[:BELONGS_TO_GENRE]->(g:Genre {name: "Hip-Hop"})
RETURN s.title, s.artist

// Find songs sharing a cultural theme
MATCH (s:Song)-[:HAS_CULTURAL_THEME]->(ct:CulturalTheme {name: "Heartbreak"})
RETURN s.title ORDER BY s.title

// What has a session asked about?
MATCH (sess:Session {session_id: "abc123"})-[:ASKED]->(s:Song)
RETURN s.title, s.artist
```

---

## API Reference

### `GET /api/health`

Returns system health, including Neo4j connectivity and vector store status.

**Response**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "services": {
    "neo4j": "healthy",
    "vector_store": "healthy"
  }
}
```

---

### `POST /api/song/ingest`

Ingests a song from YouTube. If the song is already in the database (matched by URL), returns the existing record.

**Request**
```json
{ "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID" }
```

**Response**
```json
{
  "song_id": "a1b2c3d4e5f6...",
  "title": "HUMBLE.",
  "artist": "Kendrick Lamar",
  "thumbnail": "https://img.youtube.com/vi/.../maxresdefault.jpg",
  "language": "English",
  "genres": ["Hip-Hop", "Rap"],
  "cultural_themes": ["Self-empowerment", "Social Commentary"],
  "mood": "Defiant",
  "era": "2010s",
  "message": "Song ingested successfully"
}
```

---

### `GET /api/song/{song_id}/transcript`

Retrieves the stored transcript for a song. `source` indicates whether it came from YouTube captions or ElevenLabs STT.

**Response**
```json
{
  "transcript_id": "...",
  "song_id": "...",
  "content": "Sit down, be humble...",
  "source": "youtube"
}
```

---

### `POST /api/translate`

Translates a song's lyrics using literary localization. Provide either `song_id` or `youtube_url` (the song will be auto-ingested if not already in the system).

**Request**
```json
{
  "song_id": "a1b2c3d4e5f6...",
  "target_language": "Hindi"
}
```

**Response**
```json
{
  "translation_id": "...",
  "song_id": "...",
  "target_language": "Hindi",
  "translated_lyrics": "बैठ जा, नम्र रह...",
  "translation_notes": "Adapted 'humble' to the Hindi idiom...",
  "confidence_score": 0.91
}
```

---

### `GET /api/song/{song_id}/translations`

Lists all translations stored for a song.

**Response**
```json
{
  "song_id": "...",
  "translations": [ { "target_language": "Hindi", ... }, { "target_language": "Spanish", ... } ],
  "count": 2
}
```

---

### `POST /api/rag/ask`

Ask a question about a song. The AI responds as an ethnomusicologist — explaining slang, metaphors, cultural references, and emotional context. Session history is maintained for follow-up questions within the same `session_id`.

**Request**
```json
{
  "song_id": "a1b2c3d4e5f6...",
  "session_id": "my-session-001",
  "question": "What does Kendrick mean by 'sit down, be humble'?"
}
```

**Response**
```json
{
  "answer": "Kendrick's 'sit down, be humble' operates on multiple levels...",
  "sources": [
    "Sit down, be humble / Sit down, be humble...",
    "...nobody prayin' for me..."
  ],
  "session_id": "my-session-001",
  "song_id": "a1b2c3d4e5f6..."
}
```

### Error Response (all endpoints)

```json
{
  "detail": "Song not found: a1b2c3d4e5f6",
  "error_code": "SONG_NOT_FOUND"
}
```

---

## Setup & Running

### Prerequisites

| Requirement | Notes |
|------------|-------|
| Python 3.12+ | Backend runtime |
| Node.js 18+ | Frontend runtime |
| Docker Desktop | Required for Neo4j |
| FFmpeg | Required for ElevenLabs audio fallback — install and add to PATH |

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd Sonus
```

### 2. Start Neo4j (Docker)

```bash
cd backend
docker compose up -d
```

Neo4j takes ~30 seconds to initialize. Verify at [http://localhost:7474](http://localhost:7474).

> **Login:** `neo4j` / `sonus_password` — then create/select the `sonus` database

### 3. Configure Environment

```bash
cp backend/.env.example backend/.env
# Open backend/.env and fill in your API keys (see table below)
```

### 4. Install Backend Dependencies

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 5. Run the Backend

```bash
# From the backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now live at [http://localhost:8000](http://localhost:8000).
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 6. Run the Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

### 7. First Song Ingestion

Using Swagger UI or the frontend, call:

```bash
POST /api/song/ingest
{ "youtube_url": "https://www.youtube.com/watch?v=tvTRZJ-4EyI" }
```

Copy the returned `song_id`, then ask:

```bash
POST /api/rag/ask
{
  "song_id": "<paste-id-here>",
  "session_id": "session-1",
  "question": "What is this song really about?"
}
```

---

## Environment Variables

All configuration is in `backend/.env`. Copy from `backend/.env.example`.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ | — | Groq API key — get one free at [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | | `llama-3.3-70b-versatile` | Groq model name |
| `GROQ_TEMPERATURE` | | `0.3` | LLM temperature |
| `ELEVENLABS_API_KEY` | ⚠️ | — | ElevenLabs key — required for the STT fallback when YouTube captions are missing |
| `NEO4J_URI` | | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | | `sonus_password` | Neo4j password |
| `NEO4J_DATABASE` | | `sonus` | Neo4j database name |
| `CHROMA_PERSIST_DIR` | | `./chroma_data` | Directory for persistent ChromaDB vector collections |
| `EMBEDDING_MODEL` | | `all-MiniLM-L6-v2` | HuggingFace sentence-transformer model |
| `LOG_LEVEL` | | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `CORS_ORIGINS` | | `["*"]` | Allowed CORS origins |

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

The test suite covers:
- **URL parsing** — all YouTube URL format variants
- **Transcript fallback** — YouTube success path and ElevenLabs fallback path (mocked)
- **Translation parsing** — JSON parsing, markdown fence handling, invalid JSON error
- **RAG processor** — song-not-found error, successful answer generation (mocked chain)
- **Song ingestion** — URL validation, required field checks
- **Health endpoint** — response structure verification

---

## Managing Neo4j (Docker)

```bash
# Start
docker compose up -d

# Stop (data persists)
docker compose down

# View logs
docker compose logs -f neo4j

# Stop and wipe all data
docker compose down -v

# Shell into the container
docker exec -it sonus-neo4j bash
```

**Neo4j Browser** at [http://localhost:7474](http://localhost:7474) — useful for visualizing the knowledge graph.

---

## Project Origins

Sonus began as a single-file CLI prototype (`main.py`) with a LangChain RAG pipeline for song interpretation. It was refactored into this production-grade backend architecture while preserving all original functionality and extending it with:

- FastAPI + async endpoints
- Neo4j graph persistence
- Persistent vector indexing
- ElevenLabs transcript fallback
- Literary translation engine
- Genre and cultural theme auto-classification
- Clean architecture with layered separation of concerns

---

## License

MIT — see [LICENSE](LICENSE)
