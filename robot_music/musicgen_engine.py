"""
MusicGen Engine
===============

Uses Facebook's AudioCraft MusicGen to generate music fully locally.
"""

from typing import Optional, Literal

import torch
import numpy as np

from audiocraft.models import MusicGen


# Type alias for model sizes
ModelSize = Literal["small", "medium", "large", "melody"]

# Model name mapping
MODEL_REGISTRY = {
    "small": "facebook/musicgen-small",
    "medium": "facebook/musicgen-medium",
    "large": "facebook/musicgen-large",
    "melody": "facebook/musicgen-melody",
}


class MusicGenEngine:
    """
    Wrapper around AudioCraft MusicGen models.
    
    Provides a simple interface for text-to-music generation using
    Facebook's MusicGen models.
    
    Attributes:
        model: The loaded MusicGen model
        device: The device (cuda/cpu) being used
        sample_rate: Audio sample rate (32000 Hz for MusicGen)
    """
    
    # MusicGen outputs audio at 32kHz
    SAMPLE_RATE = 32000

    def __init__(self, model_size: ModelSize = "small") -> None:
        """
        Initialize the MusicGen engine.
        
        Args:
            model_size: Size of the model to load. Options:
                - "small": Fastest, lower quality (~300M params)
                - "medium": Balanced (~1.5B params)
                - "large": Best quality (~3.3B params)
                - "melody": Melody-conditioned generation
        
        Raises:
            ValueError: If model_size is not valid
        """
        if model_size not in MODEL_REGISTRY:
            valid_sizes = list(MODEL_REGISTRY.keys())
            raise ValueError(
                f"Invalid model size: '{model_size}'. "
                f"Valid options: {valid_sizes}"
            )

        model_name = MODEL_REGISTRY[model_size]
        print(f"→ Loading MusicGen model: {model_name}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"→ Using device: {self.device}")

        self.model = MusicGen.get_pretrained(model_name).to(self.device)
        self.sample_rate = self.SAMPLE_RATE

    def generate(
        self,
        prompt: str,
        duration_seconds: int = 30,
        bpm: Optional[int] = None,
        temperature: float = 1.0,
        top_k: int = 250,
    ) -> np.ndarray:
        """
        Generate music from a text prompt.
        
        Args:
            prompt: Text description of the desired music
            duration_seconds: Length of audio to generate (max ~30s for small models)
            bpm: Beats per minute (incorporated into prompt if provided)
            temperature: Sampling temperature (higher = more creative)
            top_k: Top-k sampling parameter
        
        Returns:
            numpy array of shape (channels, samples) containing the audio waveform
        
        Example:
            >>> engine = MusicGenEngine("small")
            >>> audio = engine.generate(
            ...     prompt="upbeat electronic dance music",
            ...     duration_seconds=30,
            ...     bpm=128
            ... )
        """
        # Incorporate BPM into prompt if provided
        full_prompt = prompt
        if bpm is not None:
            full_prompt = f"{prompt}, {bpm} BPM"
        
        print(f"→ Generating music: {duration_seconds}s")
        if bpm:
            print(f"→ Target BPM: {bpm}")
        print(f"→ Prompt: {full_prompt}")

        self.model.set_generation_params(
            use_sampling=True,
            top_k=top_k,
            temperature=temperature,
            duration=duration_seconds,
        )

        # Generate audio
        with torch.inference_mode():
            wav = self.model.generate(
                descriptions=[full_prompt],
                progress=True,
            )[0]  # shape: (channels, samples)

        return wav.cpu().numpy()
    
    def get_sample_rate(self) -> int:
        """
        Get the sample rate of generated audio.
        
        Returns:
            Sample rate in Hz (32000 for MusicGen)
        """
        return self.sample_rate
