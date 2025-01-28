import sys
import warnings
import torch
import sounddevice as sd
import time
import numpy as np
import argparse
import re

from difflib import get_close_matches

# Silence specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.nn.utils.weight_norm")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn.modules.rnn")

from pathlib import Path

from voices import VoiceName, VOICE_NAMES, VOICE_DESCRIPTIONS


def clean_text(text: str) -> str:
    text = text.replace(chr(8216), "'").replace(chr(8217), "'")
    text = text.replace('«', chr(8220)).replace('»', chr(8221))
    text = text.replace(chr(8220), '"').replace(chr(8221), '"')
    # text = text.replace('(', '«').replace(')', '»')
    for a, b in zip('、。！，：；？', ',.!,:;?'):
        text = text.replace(a, b+' ')
    text = re.sub(r'[^\S \n]', ' ', text)
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'(?<=\n) +(?=\n)', '', text)
    text = re.sub(r'\bD[Rr]\.(?= [A-Z])', 'Doctor', text)
    text = re.sub(r'\b(?:Mr\.|MR\.(?= [A-Z]))', 'Mister', text)
    text = re.sub(r'\b(?:Ms\.|MS\.(?= [A-Z]))', 'Miss', text)
    text = text.replace('```', '')
    return text


def find_voice(voice_query: str) -> VoiceName | None:
    """Find the best matching voice from the query."""
    # If exact match exists, return it
    if voice_query in VOICE_NAMES:
        return voice_query  # type: ignore
    
    # Try matching without prefix
    for voice in VOICE_NAMES:
        if voice.endswith(voice_query):
            return voice
    
    # Try fuzzy matching
    matches = get_close_matches(voice_query, VOICE_NAMES, n=1, cutoff=0.6)
    return matches[0] if matches else None  # type: ignore


def list_voices() -> None:
    """Print available voices with descriptions."""
    print("\nAvailable Voices:")
    print("----------------")
    for voice in VOICE_NAMES:
        print(f"{voice:<12} - {VOICE_DESCRIPTIONS[voice]}")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Kokoro TTS - A small, high-quality text-to-speech model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Hello, world!"
  %(prog)s --voice sarah "Hello from Sarah!"
  %(prog)s --voice af_bella input.txt
  %(prog)s --debug "Hello world"     # Saves processed text chunks
  %(prog)s --silent "Hello world"    # Only saves file without playback
  %(prog)s --format opus "Hello"     # Save as compressed opus file"""
    )
    
    parser.add_argument(
        "text",
        help="Text to speak. Can be a string or a path to a text/markdown file",
        nargs="?",
        default=None
    )
    
    parser.add_argument(
        "-v", "--voice",
        help="Voice to use (can be full name like 'af_sarah' or just 'sarah')",
        default="af_sky"
    )
    
    parser.add_argument(
        "--voices",
        help="List available voices and exit",
        action="store_true"
    )

    parser.add_argument(
        "--debug",
        help="Save debug information including processed text chunks",
        action="store_true"
    )

    parser.add_argument(
        "--silent",
        help="Only save audio file without playing",
        action="store_true"
    )

    parser.add_argument(
        "-f", "--format",
        help="Output audio format (wav, opus, m4a, mp3)",
        choices=["wav", "opus", "m4a", "mp3"],
        default="wav"
    )
    
    return parser.parse_args()


def save_audio(audio: np.ndarray, path: Path, format: str, sample_rate: int = 24000) -> None:
    """Save audio in the specified format."""
    import scipy.io.wavfile as wav
    
    # Ensure audio is in correct range (-1 to 1)
    audio = np.clip(audio, -1, 1)
    
    if format == "wav":
        wav.write(str(path), sample_rate, audio)
        return
        
    # For compressed formats, we need to go through WAV first
    import tempfile
    from pydub import AudioSegment
    
    with tempfile.NamedTemporaryFile(suffix='.wav') as temp_wav:
        wav.write(temp_wav.name, sample_rate, audio)
        audio_segment = AudioSegment.from_wav(temp_wav.name)
        
        if format == "opus":
            # Opus is especially good for speech
            audio_segment.export(str(path), format="opus", 
                               parameters=["-application", "voip"])
        elif format == "m4a":
            # AAC with high quality settings
            audio_segment.export(str(path), format="ipod", 
                               parameters=["-q:a", "2"])
        elif format == "mp3":
            # MP3 with voice-optimized settings
            audio_segment.export(str(path), format="mp3",
                               parameters=["-q:a", "0", "-compression_level", "0"])


def main() -> None:
    args = parse_args()
    
    # Handle --voices flag
    if args.voices:
        list_voices()
        sys.exit(0)
    
    # Ensure text is provided if not listing voices
    if args.text is None:
        print("Error: Text argument is required unless using --voices")
        sys.exit(1)
    
    # Handle voice selection
    voice = find_voice(args.voice)
    if not voice:
        print(f"Error: Voice '{args.voice}' not found.")
        list_voices()
        sys.exit(1)
    
    print(f"Using voice: {voice} - {VOICE_DESCRIPTIONS[voice]}")
    
    # Setup paths
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)
    
    # Handle input text
    input_path = Path(args.text)
    if input_path.exists():
        text = input_path.read_text()
        is_input_md_file = input_path.suffix == '.md'
    else:
        text = args.text
        is_input_md_file = False
    text = clean_text(text)
    
    # Setup device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'Using device: {device}')
    
    # Process text
    response_chunks: list[np.ndarray] = []
    chunks = text.splitlines() if is_input_md_file else [c.strip() for c in text.split(".") if c.strip()]
    
    from kokoro import generate
    from models import build_model
    MODEL = build_model('kokoro-v0_19.pth', device)
    VOICEPACK = torch.load(f'voices/{voice}.pt', weights_only=True).to(device)
    
    for text in chunks:
        if len(text) < 2:
            continue
        result = generate(MODEL, text, VOICEPACK, lang=voice[0])
        if result is None:
            print(f"Warning: Could not generate audio for text: {text}")
            continue
        audio, _ = result
        response_chunks.append(audio)
    
    if not response_chunks:
        print("Error: No audio could be generated from the input text")
        sys.exit(1)
        
    # Concatenate and save audio
    final_audio = np.concatenate(response_chunks)
    timestamp = int(time.time())

    # Save debug file
    if args.debug:
        debug_file = output_path / f"{voice}-{timestamp}.txt"
        debug_file_text = "\n".join(chunks) if is_input_md_file else ".".join(chunks)
        debug_file.write_text(debug_file_text)
    
    # Save final audio
    output_file = output_path / f"{voice}-{timestamp}.{args.format}"
    save_audio(final_audio, output_file, args.format)
    print(f"\nSaved audio to: {output_file}")
    
    # Play the audio (unless in silent mode)
    if not args.silent:
        sd.play(final_audio, 24000)
        sd.wait()


if __name__ == "__main__":
    main()
