"""
Validator & Safety Filter
==========================
Validates JSON structure and filters NSFW/unsafe content.

Safety Level: MODERATE
- Allows: cyberpunk, dystopian, fantasy, abstract violence
- Blocks: sexual content, hate speech, graphic violence, drugs
"""

import re
from typing import Dict, Any, List, Tuple


# MODERATE safety filtering - blocks explicit content but allows edgy themes
BLOCKED_KEYWORDS = [
    # Explicit sexual content
    "porn", "pornographic", "nude", "naked", "sex", "sexual", "nsfw",
    "erotic", "xxx", "hentai", "explicit", "genital", "breast", "penis",
    "vagina", "orgasm", "fetish", "bdsm", "orgy",
    
    # Hate speech & slurs
    "nazi", "hitler", "genocide", "racist", "racial slur", "hate crime",
    "terrorist", "terrorism",
    
    # Graphic violence (abstract violence like "battle" or "ruins" is OK)
    "gore", "gory", "mutilat", "dismember", "torture", "beheading",
    "blood splatter", "corpse", "dead body", "killing spree",
    
    # Drugs & illegal activity
    "cocaine", "heroin", "meth", "methamphetamine", "drug deal",
    "trafficking", "cartel", "overdose",
    
    # Minors in unsafe context
    "child porn", "underage", "minor sexual", "pedophil"
]


def contains_blocked_content(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text contains blocked keywords.
    
    Args:
        text: Text to check
    
    Returns:
        Tuple of (is_blocked, list_of_found_keywords)
    """
    text_lower = text.lower()
    found = []
    
    for keyword in BLOCKED_KEYWORDS:
        # Use word boundaries to avoid false positives
        # e.g., "assassin" shouldn't match "ass"
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            found.append(keyword)
    
    return (len(found) > 0, found)


def sanitize_text(text: str) -> str:
    """
    Remove or replace blocked content from text.
    
    Args:
        text: Text to sanitize
    
    Returns:
        Cleaned text
    """
    is_blocked, keywords = contains_blocked_content(text)
    
    if not is_blocked:
        return text
    
    # Replace blocked keywords with safe alternatives
    replacements = {
        "nude": "minimalist",
        "naked": "bare",
        "sex": "romance",
        "sexual": "romantic",
        "erotic": "sensual",
        "gore": "intense",
        "gory": "dramatic",
        "blood": "red",
        "kill": "defeat",
        "murder": "conflict",
        "drug": "substance",
        "cocaine": "powder",
        "meth": "crystal"
    }
    
    sanitized = text
    for blocked, replacement in replacements.items():
        pattern = r'\b' + re.escape(blocked) + r'\b'
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized


def validate_config_structure(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that config has all required fields with correct types.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check top-level fields
    required_top = ["theme", "mood", "color_palette", "music", "images", "video", "youtube"]
    for field in required_top:
        if field not in config:
            errors.append(f"Missing top-level field: {field}")
    
    if "theme" in config and not isinstance(config["theme"], str):
        errors.append("Field 'theme' must be a string")
    
    if "mood" in config and not isinstance(config["mood"], str):
        errors.append("Field 'mood' must be a string")
    
    if "color_palette" in config:
        if not isinstance(config["color_palette"], list):
            errors.append("Field 'color_palette' must be a list")
        elif len(config["color_palette"]) < 2:
            errors.append("Field 'color_palette' must have at least 2 colors")
    
    # Check music section
    if "music" in config:
        music = config["music"]
        required_music = ["style", "bpm", "duration_seconds", "key", "prompt"]
        for field in required_music:
            if field not in music:
                errors.append(f"Missing music field: {field}")
        
        if "bpm" in music and not isinstance(music["bpm"], (int, float)):
            errors.append("Field 'music.bpm' must be a number")
        elif "bpm" in music and not (60 <= music["bpm"] <= 200):
            errors.append("Field 'music.bpm' must be between 60 and 200")
        
        if "duration_seconds" in music and not isinstance(music["duration_seconds"], (int, float)):
            errors.append("Field 'music.duration_seconds' must be a number")
        elif "duration_seconds" in music and not (20 <= music["duration_seconds"] <= 60):
            errors.append("Field 'music.duration_seconds' must be between 20 and 60")
    
    # Check images section
    if "images" in config:
        images = config["images"]
        required_images = ["count", "width", "height", "base_prompt", "negative_prompt"]
        for field in required_images:
            if field not in images:
                errors.append(f"Missing images field: {field}")
        
        if "count" in images and not isinstance(images["count"], int):
            errors.append("Field 'images.count' must be an integer")
        elif "count" in images and not (6 <= images["count"] <= 20):
            errors.append("Field 'images.count' must be between 6 and 20")
        
        if "width" in images and not isinstance(images["width"], int):
            errors.append("Field 'images.width' must be an integer")
        
        if "height" in images and not isinstance(images["height"], int):
            errors.append("Field 'images.height' must be an integer")
    
    # Check video section
    if "video" in config:
        video = config["video"]
        required_video = ["fps", "resolution", "transition_type", "transition_duration"]
        for field in required_video:
            if field not in video:
                errors.append(f"Missing video field: {field}")
        
        if "fps" in video and not isinstance(video["fps"], (int, float)):
            errors.append("Field 'video.fps' must be a number")
        elif "fps" in video and not (24 <= video["fps"] <= 60):
            errors.append("Field 'video.fps' must be between 24 and 60")
    
    # Check youtube section
    if "youtube" in config:
        youtube = config["youtube"]
        required_youtube = ["title", "description", "tags", "category", "privacy"]
        for field in required_youtube:
            if field not in youtube:
                errors.append(f"Missing youtube field: {field}")
        
        if "tags" in youtube and not isinstance(youtube["tags"], list):
            errors.append("Field 'youtube.tags' must be a list")
        
        if "privacy" in youtube and youtube["privacy"] not in ["public", "unlisted", "private"]:
            errors.append("Field 'youtube.privacy' must be 'public', 'unlisted', or 'private'")
    
    return (len(errors) == 0, errors)


def validate_safety(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Check all text fields for blocked content.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Tuple of (is_safe, list_of_violations)
    """
    violations = []
    
    # Check all text fields
    text_fields = [
        ("theme", config.get("theme", "")),
        ("mood", config.get("mood", "")),
        ("music.prompt", config.get("music", {}).get("prompt", "")),
        ("images.base_prompt", config.get("images", {}).get("base_prompt", "")),
        ("youtube.title", config.get("youtube", {}).get("title", "")),
        ("youtube.description", config.get("youtube", {}).get("description", ""))
    ]
    
    for field_name, text in text_fields:
        if isinstance(text, str):
            is_blocked, keywords = contains_blocked_content(text)
            if is_blocked:
                violations.append(f"Field '{field_name}' contains blocked keywords: {', '.join(keywords)}")
    
    return (len(violations) == 0, violations)


def apply_safe_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fill in missing or invalid fields with safe defaults.
    
    Args:
        config: Configuration dictionary (may be incomplete)
    
    Returns:
        Complete configuration with safe defaults
    """
    defaults = {
        "theme": "cinematic neon cityscape at night",
        "mood": "atmospheric, mysterious, energetic",
        "color_palette": ["electric blue", "neon pink", "deep purple", "cyan"],
        "music": {
            "style": "synthwave / electronic",
            "bpm": 120,
            "duration_seconds": 30,
            "key": "Am",
            "prompt": "atmospheric synthwave track with pulsing bass and ethereal pads, uplifting melody"
        },
        "images": {
            "count": 10,
            "width": 1920,
            "height": 1080,
            "base_prompt": "cinematic cityscape at night, neon lights, rain reflections, high detail, professional photography",
            "negative_prompt": "blurry, low quality, distorted, deformed, ugly"
        },
        "video": {
            "fps": 30,
            "resolution": "1920x1080",
            "transition_type": "crossfade",
            "transition_duration": 0.5
        },
        "youtube": {
            "title": "Neon Dreams - AI Generated Music Video",
            "description": "An AI-generated music video featuring synthwave music and cyberpunk visuals.",
            "tags": ["synthwave", "cyberpunk", "ai generated", "music video", "electronic"],
            "category": "10",
            "privacy": "public"
        }
    }
    
    # Deep merge: use config values if present, otherwise use defaults
    result = defaults.copy()
    
    for key in defaults:
        if key in config and isinstance(config[key], dict):
            # Merge nested dictionaries
            result[key] = {**defaults[key], **config[key]}
        elif key in config:
            # Use config value
            result[key] = config[key]
    
    return result
