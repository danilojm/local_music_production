# Local Music Production

An AI-powered local music production pipeline that uses Ollama for configuration generation and AudioCraft MusicGen for music creation.

## Overview

This project consists of two "robots" that work together:

1. **Robot Script** (`robot_script/`): Generates project configurations using local Ollama LLM
2. **Robot Music** (`robot_music/`): Creates music using Facebook's AudioCraft MusicGen

## Requirements

### System Requirements
- **Python 3.10 or 3.11** (recommended - 3.12+ may have compatibility issues)
- CUDA-capable GPU (recommended for MusicGen)
- 8GB+ RAM

### Software Dependencies
- [Ollama](https://ollama.com/download) - For local LLM inference
- PyTorch with CUDA support (for GPU acceleration)

### Dependency Compatibility Notes

⚠️ **Important**: This project has specific version requirements to avoid conflicts:

- **NumPy**: Must be <2.0.0 (NumPy 2.x is incompatible with PyTorch builds compiled with NumPy 1.x)
- **PyTorch**: Version 2.0.x or 2.1.x recommended
- **Transformers**: Version 4.31.0-4.39.x (to avoid `torch.utils._pytree` compatibility issues)

If you encounter dependency conflicts, we recommend using a fresh virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/danilojm/local_music_production.git
cd local_music_production
```

### 2. Install Ollama
Download and install from [ollama.com/download](https://ollama.com/download)

```bash
# Start Ollama service
ollama serve

# Pull the phi3 model (in another terminal)
ollama pull phi3
```

### 3. Install Robot Script Dependencies
```bash
cd robot_script
pip install -r requirements.txt
```

### 4. Install Robot Music Dependencies
```bash
cd robot_music
pip install -r requirements.txt
```

## Usage

### Step 1: Generate Configuration
```bash
cd robot_script
python run.py --output ../config/project.json
```

Options:
- `--output`: Path to save the generated configuration
- `--model`: Ollama model to use (default: phi3)

### Step 2: Generate Music
```bash
cd robot_music
python run.py --config ../config/project.json --output ../output/music.wav
```

Options:
- `--config`: Path to the project configuration JSON
- `--model`: MusicGen model size: small, medium, large, melody (default: small)
- `--output`: Path to save the generated audio

## Project Structure

```
local_music_production/
├── README.md                 # This file
├── .gitignore               # Git ignore rules
├── config/
│   └── project.json         # Generated project configuration
├── robot_script/            # Configuration generator (Robot 1)
│   ├── README.md
│   ├── requirements.txt
│   ├── run.py               # Main entry point
│   ├── ollama_client.py     # Ollama API client
│   └── validator.py         # JSON validation & safety filters
├── robot_music/             # Music generator (Robot 2)
│   ├── README.md
│   ├── requirements.txt
│   ├── run.py               # Main entry point
│   └── musicgen_engine.py   # MusicGen wrapper
└── output/                  # Generated outputs (not tracked)
    └── music.wav
```

## Configuration Format

The generated `project.json` includes:

```json
{
  "theme": "A futuristic cityscape at sunset",
  "mood": "energetic yet mysterious",
  "color_palette": ["neon green", "vibrant purple"],
  "music": {
    "style": "electro-pop synthwave",
    "bpm": 120,
    "duration_seconds": 30,
    "key": "Am",
    "prompt": "A smooth melody with catchy hooks"
  },
  "images": { ... },
  "video": { ... },
  "youtube": { ... }
}
```

## Supported Models

### Ollama Models
- `phi3` (recommended for low RAM)
- `tinyllama` (very fast, smaller)
- `llama3.1` (best quality, needs 5GB+ RAM)
- `mistral` (fast, creative)

### MusicGen Models
- `small` - Fast, lower quality (~300M params)
- `medium` - Balanced (~1.5B params)
- `large` - High quality (~3.3B params)
- `melody` - Melody-conditioned generation

## Troubleshooting

### Ollama not running
```
Error: Ollama is not running!
```
Solution: Start Ollama with `ollama serve`

### Model not found
```
Error: model 'phi3' not found
```
Solution: Pull the model with `ollama pull phi3`

### CUDA out of memory
Try using a smaller MusicGen model:
```bash
python run.py --model small --config ../config/project.json
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
