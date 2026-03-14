import io
import logging

logger = logging.getLogger(__name__)


class AudioHelper:
    """Utility functions for audio processing."""

    @staticmethod
    def text_to_speech_bytes(text: str, language: str = 'en', speed: float = 1.0) -> bytes:
        """
        Convert text to speech and return audio bytes.
        """
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=language, slow=(speed < 0.8))
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            logger.error(f"TTS conversion failed: {e}")
            return b''

    @staticmethod
    def get_urgency_tone(urgency: str) -> dict:
        """
        Get audio parameters based on urgency level.
        """
        tones = {
            'normal': {'speed': 1.0, 'volume': 0.7, 'repeat': 1},
            'caution': {'speed': 1.1, 'volume': 0.8, 'repeat': 1},
            'warning': {'speed': 1.2, 'volume': 0.9, 'repeat': 2},
            'stop': {'speed': 1.3, 'volume': 1.0, 'repeat': 3}
        }
        return tones.get(urgency, tones['normal'])