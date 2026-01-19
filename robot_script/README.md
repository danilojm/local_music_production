# Robot Script - Configuration Generator

This module generates project configurations using local Ollama LLM.

## Features

- Local LLM integration via Ollama
- JSON structure validation
- NSFW/content safety filtering (moderate level)
- Auto-retry on generation failures
- Safe fallback defaults

## Requirements

- Python 3.10+
- Ollama installed and running
- Model pulled (e.g., `ollama pull phi3`)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage
python run.py --output ../config/project.json

# Specify a different model
python run.py --output ../config/project.json --model llama3.1
```

## Configuration Output

The script generates a JSON file with:
- Theme and mood
- Color palette
- Music parameters (style, BPM, duration, key, prompt)
- Image generation settings
- Video settings
- YouTube metadata

## Safety Filtering

The validator applies moderate safety filtering:
- **Allowed**: Cyberpunk, dystopian, fantasy, abstract violence
- **Blocked**: Sexual content, hate speech, graphic violence, drugs

## Files

- `run.py` - Main entry point
- `ollama_client.py` - HTTP client for Ollama API
- `validator.py` - JSON validation and safety filters
