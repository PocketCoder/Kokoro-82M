---
license: apache-2.0
language:
- en
base_model:
- yl4579/StyleTTS2-LJSpeech
pipeline_tag: text-to-speech
---
<audio controls><source src="https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/HEARME.wav" type="audio/wav"></audio>

**Kokoro** is a frontier TTS model for its size of **82 million parameters** (text in/audio out).

On 25 Dec 2024, Kokoro v0.19 weights were permissively released in full fp32 precision along with 2 voicepacks (Bella and Sarah), all under an Apache 2.0 license.

At the time of release, Kokoro v0.19 was the #1🥇 ranked model in [TTS Spaces Arena](https://huggingface.co/spaces/Pendrokar/TTS-Spaces-Arena). With 82M params trained for <20 epochs on <100 total hours of audio, Kokoro achieved higher Elo in this single-voice Arena setting over models such as:
- XTTS v2: 467M, CPML, >10k hours
- Edge TTS: Microsoft, proprietary
- MetaVoice: 1.2B, Apache, 100k hours
- Parler Mini: 880M, Apache, 45k hours
- Fish Speech: ~500M, CC-BY-NC-SA, 1M hours

Kokoro's ability to top this Elo ladder using relatively low compute and data suggests that the scaling law for traditional TTS models might have a steeper slope than previously expected.

You can find a hosted demo at [hf.co/spaces/hexgrad/Kokoro-TTS](https://huggingface.co/spaces/hexgrad/Kokoro-TTS).

### Usage

The following can be run in a single cell on [Google Colab](https://colab.research.google.com/).
```py
# 1️⃣ Install dependencies silently
!git clone https://huggingface.co/hexgrad/Kokoro-82M
%cd Kokoro-82M
!apt-get -qq -y install espeak-ng > /dev/null 2>&1
!pip install -q phonemizer torch transformers scipy munch

# 2️⃣ Build the model and load the default voicepack
from models import build_model
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL = build_model('kokoro-v0_19.pth', device)
VOICEPACK = torch.load('voices/af.pt', weights_only=True).to(device)

# 3️⃣ Call generate, which returns a 24khz audio waveform and a string of output phonemes
from kokoro import generate
text = "How could I know? It's an unanswerable question. Like asking an unborn child if they'll lead a good life. They haven't even been born."
audio, out_ps = generate(MODEL, text, VOICEPACK)

# 4️⃣ Display the 24khz audio and print the output phonemes
from IPython.display import display, Audio
display(Audio(data=audio, rate=24000, autoplay=True))
print(out_ps)
```
This inference code was quickly hacked together on Christmas Day. It is not clean code and leaves a lot of room for improvement. If you'd like to contribute, feel free to open a PR.

### Model Description

No affiliation can be assumed between parties on different lines.

**Architecture:**
- StyleTTS 2: https://arxiv.org/abs/2306.07691
- ISTFTNet: https://arxiv.org/abs/2203.02395
- Decoder only: no diffusion, no encoder release

**Architected by:** Li et al @ https://github.com/yl4579/StyleTTS2

**Trained by**: `@rzvzn` on Discord

**Supported Languages:** English

**Model SHA256 Hash:** `3b0c392f87508da38fad3a2f9d94c359f1b657ebd2ef79f9d56d69503e470b0a`

**Model Release Date:**
- v0.19, Bella, Sarah: 25 Dec 2024

**Licenses:**
- Apache 2.0 weights in this repository
- MIT inference code in [spaces/hexgrad/Kokoro-TTS](https://huggingface.co/spaces/hexgrad/Kokoro-TTS) adapted from [yl4579/StyleTTS2](https://github.com/yl4579/StyleTTS2)
- GPLv3 dependency in [espeak-ng](https://github.com/espeak-ng/espeak-ng)

The inference code was originally MIT licensed by the paper author. Note that this card applies only to this model, Kokoro. Original models published by the paper author can be found at [hf.co/yl4579](https://huggingface.co/yl4579).

### Evaluation

**Metric:** Elo rating

**Leaderboard:** [hf.co/spaces/Pendrokar/TTS-Spaces-Arena](https://huggingface.co/spaces/Pendrokar/TTS-Spaces-Arena)

![TTS-Spaces-Arena-25-Dec-2024](TTS-Spaces-Arena-25-Dec-2024.png)

The voice ranked in the Arena is a 50-50 mix of Bella and Sarah. For your convenience, this mix is included in this repository as `af.pt`, but you can trivially reproduce it like this:

```py
import torch
bella = torch.load('voices/af_bella.pt', weights_only=True)
sarah = torch.load('voices/af_sarah.pt', weights_only=True)
af = torch.mean(torch.stack([bella, sarah]), dim=0)
assert torch.equal(af, torch.load('voices/af.pt', weights_only=True))
```

### Training Details

**Compute:** Kokoro was trained on A100 80GB vRAM instances rented from [Vast.ai](https://cloud.vast.ai/?ref_id=79907) (referral link). Vast was chosen over other compute providers due to its competitive on-demand hourly rates. The average hourly cost for the A100 80GB vRAM instances used for training was below $1/hr per GPU, which was around half the quoted rates from other providers at the time.

**Data:** Kokoro was trained exclusively on **permissive/non-copyrighted audio data** and IPA phoneme labels. Examples of permissive/non-copyrighted audio include:
- Public domain audio
- Audio licensed under Apache, MIT, etc
- Synthetic audio<sup>[1]</sup> generated by closed<sup>[2]</sup> TTS models from large providers<br/>
[1] https://copyright.gov/ai/ai_policy_guidance.pdf<br/>
[2] No synthetic audio from open TTS models or "custom voice clones"

**Epochs:** Less than **20 epochs**

**Total Dataset Size:** Less than **100 hours** of audio

### Limitations

Kokoro v0.19 is limited in some ways, in its training set and architecture:
- [Data] Lacks voice cloning capability, likely due to small <100h training set
- [Arch] Relies on external g2p (espeak-ng), which introduces a class of g2p failure modes
- [Data] Training dataset is mostly long-form reading and narration, not conversation
- [Arch] At 82M params, Kokoro almost certainly falls to a well-trained 1B+ param diffusion transformer, or a many-billion-param MLLM like GPT-4o / Gemini 2.0 Flash
- [Data] Multilingual capability is architecturally feasible, but training data is almost entirely English

**Will the other voicepacks be released?** There is currently no release date scheduled for the other voicepacks, but in the meantime you can try them in the hosted demo at [hf.co/spaces/hexgrad/Kokoro-TTS](https://huggingface.co/spaces/hexgrad/Kokoro-TTS).

### Acknowledgements
- [@yl4579](https://huggingface.co/yl4579) for architecting StyleTTS 2
- [@Pendrokar](https://huggingface.co/Pendrokar) for adding Kokoro as a contender in the TTS Spaces Arena

### Model Card Contact

`@rzvzn` on Discord

```py
# TODO: Add Discord server
```

<img src="https://static0.gamerantimages.com/wordpress/wp-content/uploads/2024/08/terminator-zero-41-1.jpg" width="400" alt="kokoro" />