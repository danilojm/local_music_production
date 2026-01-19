# Robot Music - Music Generator

This module generates music using Facebook's AudioCraft MusicGen.

## Features

- Local music generation with MusicGen
- Multiple model sizes (small, medium, large, melody)
- Text-to-music generation
- Automatic GPU/CPU detection

## Requirements

- Python 3.10+
- PyTorch with CUDA support (recommended)
- 8GB+ RAM (16GB+ for large models)

## Installation

```bash
pip install -r requirements.txt
```

**Note**: For GPU acceleration, install PyTorch with CUDA first:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Usage

```bash
# Basic usage with default settings
python run.py --config ../config/project.json

# Specify model size and output path
python run.py --config ../config/project.json --model medium --output ../output/music.wav
```

## Model Sizes

| Model | Parameters | VRAM | Quality |
|-------|------------|------|--------|
| small | ~300M | 2GB | Good |
| medium | ~1.5B | 5GB | Better |
| large | ~3.3B | 10GB | Best |
| melody | ~1.5B | 5GB | Melody-conditioned |

## Configuration

The script reads music parameters from `project.json`:

```json
{
  "music": {
    "style": "synthwave",
    "bpm": 120,
    "duration_seconds": 30,
    "key": "Am",
    "prompt": "atmospheric synthwave with pulsing bass"
  }
}
```

## Files

- `run.py` - Main entry point
- `musicgen_engine.py` - MusicGen model wrapper
