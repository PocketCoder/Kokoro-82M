# Mac OS

## Install dependencies

```bash
brew install espeak-ng
```

> If you're using custom paths, you'll need to update the `kokoro.py` file, line 12, to point to your espeak-ng library. The default location is `/opt/homebrew/Cellar/espeak-ng/1.52.0/lib/libespeak-ng.1.dylib` which is referenced as `EspeakWrapper.set_library('/opt/homebrew/Cellar/espeak-ng/1.52.0/lib/libespeak-ng.1.dylib')` in the `kokoro.py` file.

### Python Dependencies

I highly recommend using [uv (https://docs.astral.sh/uv)](https://docs.astral.sh/uv/) for your Python package/python version manager.

#### **Using uv**

Until a `pyproject.toml` file is added you'll need to install dependencies via `uv pip install ...`.

```bash
uv venv
. .venv/bin/activate

uv pip install --requirements requirements.txt
```

Alternatively, install the packages individually

```bash
# Individual dependencies
uv pip install phonemizer torch transformers scipy munch sounddevice opuslib pydub

# For notebook development (optional)
uv pip install ipykernel ipywidgets

```

#### **Using pip**

```bash
python -m venv .venv

. .venv/bin/activate

pip install --requirements requirements.txt
```

## Run the model

The model can be run using either `uv` or regular Python. Here's how to use it:

### Basic Usage

```bash
# Using uv
uv run python main.py "Hello, world!"

# Using Python directly
python main.py "Hello, world!"
```

### Command Line Options

```
main.py [options] [text]
```

#### Arguments
- `text`: Text to speak or path to a text/markdown file

#### Options
- `-v, --voice VOICE`: Voice to use (e.g., 'af_sarah' or just 'sarah')
- `-f, --format FORMAT`: Output format [wav, opus, m4a, mp3]
- `--voices`: List available voices and exit
- `--debug`: Save processed text chunks for debugging
- `--silent`: Save file without audio playback
- `-h, --help`: Show help message

### Examples

```bash
# List available voices
uv run python main.py --voices

# Use a specific voice
uv run python main.py --voice sarah "Hello from Sarah!"

# Process a text file with British female voice
uv run python main.py --voice bf_emma input.txt

# Save as compressed opus format (good for speech)
uv run python main.py --format opus "Hello world"

# Save file without playing audio
uv run python main.py --silent "Hello world"

# Debug mode with compressed audio
uv run python main.py --debug --format opus "Hello world"
```

All examples above can also be run with regular Python by replacing `uv run python` with just `python`.

### Output

The model will:
1. Generate audio in the specified format (default: wav)
2. Save it to the `output/` directory with timestamp
3. Play the audio (unless `--silent` is used)
4. Save debug info if `--debug` is enabled

## Backward Compatibility

The remaining notes are for the original HF repo: https://huggingface.co/hexgrad/Kokoro-82M. See [README](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/README.md) for details.

> These changes have already been implemented in this fork.

## Modify the path to the espeak-ng library

Edit the file `kokoro.py` and add the following lines to the top of the file:

```python
from phonemizer.backend.espeak.wrapper import EspeakWrapper
EspeakWrapper.set_library('/opt/homebrew/Cellar/espeak-ng/1.52.0/lib/libespeak-ng.1.dylib')

# Existing code...
import phonemizer
