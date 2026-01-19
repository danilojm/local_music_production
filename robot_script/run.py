#!/usr/bin/env python3
"""
ROBOT 1: SCRIPT GENERATOR
==========================

Generates project configuration using Ollama (local AI).

Features:
- Ollama integration for creative generation
- JSON structure validation
- NSFW filtering (moderate level)
- Auto-retry on failure (up to 3 attempts)
- Safe fallback defaults
- JSON cleaning (removes inline comments)

Requirements:
- Ollama installed and running: https://ollama.com/download
- Model pulled: ollama pull phi3

Usage:
    python run.py --output config/project.json
    python run.py --output config/project.json --model phi3
"""

import argparse
import json
import random
import re
import string
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ollama_client import OllamaClient
from validator import (
    validate_config_structure,
    validate_safety,
    apply_safe_defaults,
)


def generate_project_id() -> str:
    """
    Generate a unique project identifier.
    
    Returns:
        Project ID in format: project_YYYYMMDD_HHMMSS_xxxxxx
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"project_{timestamp}_{random_suffix}"


def build_ollama_prompt() -> str:
    """
    Construct the prompt for Ollama.
    
    Returns:
        Formatted prompt string instructing LLM to generate valid JSON config
    """
    return """You are a creative AI assistant that generates configurations for AI music video projects.

Your task: Generate a COMPLETE project configuration as a VALID JSON object.

CRITICAL: Respond with PURE JSON only. No explanations, no markdown, no comments, no extra text.

Required JSON structure:

{
  "theme": "a short, creative theme description",
  "mood": "emotional tone (e.g., energetic, mysterious, calm)",
  "color_palette": ["color1", "color2", "color3"],
  "music": {
    "style": "music genre/style",
    "bpm": 120,
    "duration_seconds": 30,
    "key": "Am",
    "prompt": "detailed description for music generation"
  },
  "images": {
    "count": 10,
    "width": 1920,
    "height": 1080,
    "base_prompt": "detailed Stable Diffusion prompt",
    "negative_prompt": "what to avoid"
  },
  "video": {
    "fps": 30,
    "resolution": "1920x1080",
    "transition_type": "crossfade",
    "transition_duration": 0.5
  },
  "youtube": {
    "title": "catchy video title",
    "description": "1-3 sentence description",
    "tags": ["tag1", "tag2", "tag3"],
    "category": "10",
    "privacy": "public"
  }
}

Rules:
- duration_seconds: 20-60
- image count: 6-20
- bpm: 60-200
- fps: 24-60
- width: 1920, height: 1080
- NO inline comments in JSON
- NO extra text outside JSON
- Theme must be YouTube-safe

Generate ONLY the JSON:"""


def extract_json_from_response(response: str) -> str:
    """
    Extract JSON from LLM response, handling markdown code blocks and inline comments.
    
    Args:
        response: Raw response from Ollama
    
    Returns:
        Cleaned JSON string ready for parsing
    """
    # Remove markdown code blocks if present
    cleaned = response.strip()
    
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    cleaned = cleaned.strip()
    
    # Remove inline comments like: "category": "10" (Music & Entertainment)
    # Pattern: matches anything in parentheses after a quoted value
    cleaned = re.sub(r'"\s*\([^)]+\)\s*,', '",', cleaned)
    cleaned = re.sub(r'"\s*\([^)]+\)\s*}', '"}', cleaned)
    cleaned = re.sub(r'"\s*\([^)]+\)\s*\]', '"]', cleaned)
    
    return cleaned


def generate_config_with_ollama(
    client: OllamaClient, 
    max_attempts: int = 3
) -> dict[str, Any]:
    """
    Generate configuration using Ollama with validation and retry logic.
    
    Args:
        client: OllamaClient instance
        max_attempts: Maximum number of generation attempts
    
    Returns:
        Valid configuration dictionary
    """
    prompt = build_ollama_prompt()
    json_text = ""  # Initialize for error handling
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n{'='*60}")
        print(f"GENERATION ATTEMPT {attempt}/{max_attempts}")
        print(f"{'='*60}")
        
        try:
            # Generate from Ollama
            print("→ Asking Ollama to generate configuration...")
            raw_response = client.generate(prompt, temperature=0.8)
            
            # Extract and clean JSON
            print("→ Cleaning response...")
            json_text = extract_json_from_response(raw_response)
            
            # Parse JSON
            print("→ Parsing JSON...")
            config = json.loads(json_text)
            
            # Validate structure
            print("→ Validating structure...")
            is_valid, errors = validate_config_structure(config)
            if not is_valid:
                print("✗ Structure validation failed:")
                for error in errors:
                    print(f"  - {error}")
                if attempt < max_attempts:
                    print("→ Retrying with more explicit prompt...")
                    continue
                else:
                    print("→ Using safe defaults for invalid fields...")
                    config = apply_safe_defaults(config)
            
            # Validate safety
            print("→ Checking content safety...")
            is_safe, violations = validate_safety(config)
            if not is_safe:
                print("✗ Safety check failed:")
                for violation in violations:
                    print(f"  - {violation}")
                if attempt < max_attempts:
                    print("→ Regenerating with stricter guidelines...")
                    continue
                else:
                    print("→ Applying safe defaults...")
                    config = apply_safe_defaults(config)
            
            print("✓ Configuration generated successfully!")
            return config
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing failed: {e}")
            preview = json_text[:200] if json_text else "(empty response)"
            print(f"  Raw response preview: {preview}...")
            if attempt < max_attempts:
                print("→ Retrying...")
            else:
                print("→ All attempts failed, using safe defaults...")
                return apply_safe_defaults({})
        
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            if attempt < max_attempts:
                print("→ Retrying...")
            else:
                print("→ All attempts failed, using safe defaults...")
                return apply_safe_defaults({})
    
    # Fallback (should not reach here normally)
    print("✗ All generation attempts failed")
    print("→ Using safe defaults...")
    return apply_safe_defaults({})


def main() -> int:
    """
    Main entry point for the script generator.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate project configuration using Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --output config/project.json
  python run.py --output config/project.json --model phi3
  python run.py --output config/project.json --model tinyllama

Supported models (must be pulled first with 'ollama pull'):
  - phi3 (recommended for low RAM)
  - tinyllama (very fast, smaller)
  - llama3.1 (best quality, needs 5GB+ RAM)
  - mistral (fast, creative)
        """
    )
    
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output JSON file path"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="phi3",
        help="Ollama model name (default: phi3)"
    )
    
    args = parser.parse_args()
    
    # Prepare output path
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("ROBOT 1: SCRIPT GENERATOR")
    print("="*60)
    print(f"Model:  {args.model}")
    print(f"Output: {output_path}")
    print("="*60)
    
    # Initialize Ollama client
    print("\n→ Initializing Ollama client...")
    client = OllamaClient(model=args.model)
    
    # Check if Ollama is running
    print("→ Checking if Ollama is running...")
    if not client.is_running():
        print("\n✗ ERROR: Ollama is not running!")
        print("\nSetup instructions:")
        print("  1. Install Ollama: https://ollama.com/download")
        print("  2. Start Ollama: ollama serve")
        print(f"  3. Pull model: ollama pull {args.model}")
        print("\nThen run this script again.")
        return 1
    
    print("✓ Ollama is running")
    
    # Generate configuration
    config = generate_config_with_ollama(client, max_attempts=3)
    
    # Add metadata
    config["project_id"] = generate_project_id()
    config["created_at"] = datetime.now(timezone.utc).isoformat()
    config["generator"] = {
        "robot": "script_generator",
        "model": args.model,
        "version": "1.0"
    }
    
    # Save to file
    print(f"\n→ Saving configuration to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("✓ CONFIGURATION GENERATED SUCCESSFULLY")
    print("="*60)
    print(f"Project ID: {config['project_id']}")
    print(f"Theme: {config['theme']}")
    print(f"Music style: {config['music']['style']}")
    print(f"Duration: {config['music']['duration_seconds']}s")
    print(f"Images: {config['images']['count']}")
    print(f"Video title: {config['youtube']['title']}")
    print(f"\nSaved to: {output_path}")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
