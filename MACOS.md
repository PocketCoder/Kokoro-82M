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
```
