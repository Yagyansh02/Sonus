"""
ElevenLabs Speech-to-Text service.

Provides transcript fallback when YouTube captions are unavailable.
Uses the ElevenLabs Scribe v2 model for high-accuracy transcription.
"""

from pathlib import Path

from app.config.settings import get_settings
from app.utils.logger import get_logger
from app.utils.exceptions import ElevenLabsError

logger = get_logger("services.elevenlabs")


def transcribe_audio(audio_path: Path) -> str:
    """
    Transcribe an audio file using ElevenLabs Scribe v2.

    Args:
        audio_path: Path to the audio file (MP3, M4A, etc.)

    Returns:
        Transcribed text content.

    Raises:
        ElevenLabsError: If the API key is missing or the request fails.
    """
    settings = get_settings()

    if not settings.ELEVENLABS_API_KEY:
        raise ElevenLabsError(
            "ELEVENLABS_API_KEY not configured. "
            "Cannot use speech-to-text fallback."
        )

    logger.info(f"Transcribing audio via ElevenLabs: {audio_path.name}")

    try:
        from elevenlabs.client import ElevenLabs

        client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

        with open(audio_path, "rb") as audio_file:
            transcription = client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v2",
                tag_audio_events=False,
                diarize=False,
            )

        # The API returns an object with a .text attribute
        text = transcription.text if hasattr(transcription, "text") else str(transcription)

        if not text or not text.strip():
            raise ElevenLabsError("ElevenLabs returned an empty transcript")

        logger.info(f"ElevenLabs transcription complete: {len(text)} characters")
        return text.strip()

    except ElevenLabsError:
        raise
    except Exception as e:
        logger.error(f"ElevenLabs transcription failed: {e}")
        raise ElevenLabsError(detail=str(e))
