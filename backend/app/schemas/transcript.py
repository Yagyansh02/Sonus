from pydantic import BaseModel


class TranscriptResponse(BaseModel):
    transcript_id: str
    song_id: str
    content: str
    source: str = "youtube"
