"""Voice types and constants for Kokoro TTS."""

from typing import TypeAlias, Literal

VoiceName: TypeAlias = Literal[
    'af', 'af_bella', 'af_sarah', 'am_adam', 'am_michael',
    'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
    'af_nicole', 'af_sky'
]

# Language code for phonemization
LanguageCode: TypeAlias = Literal['a', 'b']  # 'a' for US English, 'b' for British English

VOICE_NAMES: list[VoiceName] = [
    'af', 'af_bella', 'af_sarah', 'am_adam', 'am_michael',
    'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
    'af_nicole', 'af_sky'
]

# Voice descriptions for better UX
VOICE_DESCRIPTIONS: dict[VoiceName, str] = {
    'af': 'Adult Female (Neutral)',
    'af_bella': 'Adult Female - Bella (Warm)',
    'af_sarah': 'Adult Female - Sarah (Professional)',
    'am_adam': 'Adult Male - Adam (Friendly)',
    'am_michael': 'Adult Male - Michael (Deep)',
    'bf_emma': 'British Female - Emma (Proper)',
    'bf_isabella': 'British Female - Isabella (Soft)',
    'bm_george': 'British Male - George (Formal)',
    'bm_lewis': 'British Male - Lewis (Casual)',
    'af_nicole': 'Adult Female - Nicole (Whisper)',
    'af_sky': 'Adult Female - Sky (Bright)'
}

__all__ = ['VoiceName', 'LanguageCode', 'VOICE_NAMES', 'VOICE_DESCRIPTIONS']
