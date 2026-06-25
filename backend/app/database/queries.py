"""
Cypher query constants for Neo4j CRUD operations.

All graph queries are centralized here so they can be reviewed,
optimized, and tested independently of the service layer.

═══ GRAPH MODEL ═══

Nodes:
  (:Song)           – primary entity
  (:Artist)         – song creator
  (:Transcript)     – lyrics text
  (:Translation)    – translated lyrics
  (:Session)        – conversation session
  (:Genre)          – music genre
  (:CulturalTheme)  – thematic tag
  (:Chunk)          – lyric chunk with embedding vector

Relationships:
  (Artist)-[:CREATED]->(Song)
  (Song)-[:HAS_TRANSCRIPT]->(Transcript)
  (Song)-[:HAS_TRANSLATION]->(Translation)
  (Song)-[:BELONGS_TO_GENRE]->(Genre)
  (Song)-[:HAS_CULTURAL_THEME]->(CulturalTheme)
  (Session)-[:ASKED]->(Song)
  (Song)-[:HAS_CHUNK]->(Chunk)
"""

# ── Constraints & Indexes (run once at startup) ──────────────────

SETUP_CONSTRAINTS = [
    "CREATE CONSTRAINT song_id_unique IF NOT EXISTS FOR (s:Song) REQUIRE s.song_id IS UNIQUE",
    "CREATE CONSTRAINT artist_name_unique IF NOT EXISTS FOR (a:Artist) REQUIRE a.name IS UNIQUE",
    "CREATE CONSTRAINT transcript_id_unique IF NOT EXISTS FOR (t:Transcript) REQUIRE t.transcript_id IS UNIQUE",
    "CREATE CONSTRAINT translation_id_unique IF NOT EXISTS FOR (t:Translation) REQUIRE t.translation_id IS UNIQUE",
    "CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:Session) REQUIRE s.session_id IS UNIQUE",
    "CREATE CONSTRAINT genre_name_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
    "CREATE CONSTRAINT theme_name_unique IF NOT EXISTS FOR (ct:CulturalTheme) REQUIRE ct.name IS UNIQUE",
    "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.chunk_id IS UNIQUE",
]

# ── Vector Index (run once at startup) ──────────────────────────
# all-MiniLM-L6-v2 produces 384-dimensional dense vectors.
# This index is kept for potential future cross-song graph traversal;
# per-song RAG uses exact KNN (see SEARCH_SIMILAR_CHUNKS).

SETUP_VECTOR_INDEX = """
CREATE VECTOR INDEX chunk_embedding_index IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}}
"""


# ── Song ─────────────────────────────────────────────────────────

CREATE_SONG = """
MERGE (s:Song {song_id: $song_id})
ON CREATE SET
    s.title = $title,
    s.youtube_url = $youtube_url,
    s.thumbnail = $thumbnail,
    s.language = $language,
    s.mood = $mood,
    s.era = $era,
    s.created_at = datetime()
ON MATCH SET
    s.title = $title,
    s.thumbnail = $thumbnail,
    s.language = $language,
    s.mood = $mood,
    s.era = $era
RETURN s
"""

GET_SONG_BY_ID = """
MATCH (s:Song {song_id: $song_id})
OPTIONAL MATCH (a:Artist)-[:CREATED]->(s)
OPTIONAL MATCH (s)-[:BELONGS_TO_GENRE]->(g:Genre)
OPTIONAL MATCH (s)-[:HAS_CULTURAL_THEME]->(ct:CulturalTheme)
RETURN s, a.name AS artist,
       collect(DISTINCT g.name) AS genres,
       collect(DISTINCT ct.name) AS cultural_themes
"""

GET_SONG_BY_URL = """
MATCH (s:Song {youtube_url: $youtube_url})
OPTIONAL MATCH (a:Artist)-[:CREATED]->(s)
OPTIONAL MATCH (s)-[:BELONGS_TO_GENRE]->(g:Genre)
OPTIONAL MATCH (s)-[:HAS_CULTURAL_THEME]->(ct:CulturalTheme)
RETURN s, a.name AS artist,
       collect(DISTINCT g.name) AS genres,
       collect(DISTINCT ct.name) AS cultural_themes
"""


# ── Artist ───────────────────────────────────────────────────────

CREATE_ARTIST_AND_LINK = """
MERGE (a:Artist {name: $artist_name})
WITH a
MATCH (s:Song {song_id: $song_id})
MERGE (a)-[:CREATED]->(s)
RETURN a
"""


# ── Genre ────────────────────────────────────────────────────────

LINK_SONG_TO_GENRE = """
MERGE (g:Genre {name: $genre_name})
WITH g
MATCH (s:Song {song_id: $song_id})
MERGE (s)-[:BELONGS_TO_GENRE]->(g)
RETURN g
"""


# ── Cultural Theme ───────────────────────────────────────────────

LINK_SONG_TO_CULTURAL_THEME = """
MERGE (ct:CulturalTheme {name: $theme_name})
WITH ct
MATCH (s:Song {song_id: $song_id})
MERGE (s)-[:HAS_CULTURAL_THEME]->(ct)
RETURN ct
"""


# ── Transcript ───────────────────────────────────────────────────

CREATE_TRANSCRIPT = """
MERGE (t:Transcript {transcript_id: $transcript_id})
ON CREATE SET
    t.content = $content,
    t.source = $source,
    t.created_at = datetime()
WITH t
MATCH (s:Song {song_id: $song_id})
MERGE (s)-[:HAS_TRANSCRIPT]->(t)
RETURN t
"""

GET_TRANSCRIPT_BY_SONG_ID = """
MATCH (s:Song {song_id: $song_id})-[:HAS_TRANSCRIPT]->(t:Transcript)
RETURN t
"""


# ── Translation ──────────────────────────────────────────────────

CREATE_TRANSLATION = """
MERGE (tr:Translation {translation_id: $translation_id})
ON CREATE SET
    tr.target_language = $target_language,
    tr.translated_lyrics = $translated_lyrics,
    tr.notes = $notes,
    tr.confidence_score = $confidence_score,
    tr.created_at = datetime()
WITH tr
MATCH (s:Song {song_id: $song_id})
MERGE (s)-[:HAS_TRANSLATION]->(tr)
RETURN tr
"""

GET_TRANSLATIONS_BY_SONG_ID = """
MATCH (s:Song {song_id: $song_id})-[:HAS_TRANSLATION]->(tr:Translation)
RETURN tr
ORDER BY tr.created_at DESC
"""


# ── Session ──────────────────────────────────────────────────────

CREATE_SESSION = """
MERGE (sess:Session {session_id: $session_id})
ON CREATE SET sess.created_at = datetime()
RETURN sess
"""

LINK_SESSION_TO_SONG = """
MATCH (sess:Session {session_id: $session_id})
MATCH (s:Song {song_id: $song_id})
MERGE (sess)-[:ASKED]->(s)
RETURN sess, s
"""


# ── Chunk (Vector Embeddings) ─────────────────────────────────────

UPSERT_CHUNK = """
MERGE (c:Chunk {chunk_id: $chunk_id})
ON CREATE SET
    c.song_id    = $song_id,
    c.content    = $content,
    c.embedding  = $embedding,
    c.chunk_index = $chunk_index,
    c.created_at = datetime()
WITH c
MATCH (s:Song {song_id: $song_id})
MERGE (s)-[:HAS_CHUNK]->(c)
RETURN c
"""

# Exact KNN: traverse the graph to this song's chunks only, then
# compute cosine similarity in real-time.  Avoids the post-filtering
# trap of global ANN search — a single song has only a few dozen chunks,
# so exact nearest-neighbour is both correct and fast.
SEARCH_SIMILAR_CHUNKS = """
MATCH (s:Song {song_id: $song_id})-[:HAS_CHUNK]->(c:Chunk)
WITH c, vector.similarity.cosine(c.embedding, $query_embedding) AS score
ORDER BY score DESC
LIMIT $k
RETURN c.content AS content, c.chunk_index AS chunk_index, score
"""

SONG_HAS_CHUNKS = """
MATCH (s:Song {song_id: $song_id})-[:HAS_CHUNK]->(c:Chunk)
RETURN count(c) AS chunk_count
"""

DELETE_SONG_CHUNKS = """
MATCH (s:Song {song_id: $song_id})-[:HAS_CHUNK]->(c:Chunk)
DETACH DELETE c
"""
