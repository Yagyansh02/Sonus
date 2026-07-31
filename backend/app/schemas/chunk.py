"""
LyricChunk DTO.

Internal Data Transfer Object for passing chunk data between
vector_service.chunk_and_embed() and neo4j_service.store_chunks().

Using a typed Pydantic model instead of a plain dict guarantees the
shape of the data at every boundary and surfaces key-name typos at
import time rather than as KeyErrors at runtime.
"""

from pydantic import BaseModel, Field


class LyricChunk(BaseModel):
    """A single embedded lyric chunk ready to be stored in Neo4j."""

    chunk_id: str = Field(..., description="Unique UUID hex identifier for the chunk")
    song_id: str = Field(..., description="Owning song's ID")
    content: str = Field(..., description="Chunk text")
    embedding: list[float] = Field(..., description="384-dim HuggingFace embedding vector")
    chunk_index: int = Field(..., description="Positional order within the song (0-indexed)")
    section_type: str = Field(
        default="Unknown",
        description="Musical section label (e.g. 'Verse 1', 'Chorus', 'Bridge'). "
                    "Set by lyrics_structurizer; defaults to 'Unknown' on fallback.",
    )
