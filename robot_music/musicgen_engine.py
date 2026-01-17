"""
MusicGen Engine
===============

Uses Facebook's AudioCraft MusicGen to generate music fully locally.
"""

import torch
import torchaudio
import numpy as np
import soundfile as sf

from audiocraft.models import MusicGen


class MusicGenEngine:
    """
    Wrapper around AudioCraft MusicGen models.
    """

    def __init__(self, model_size="small"):
        """
        Args:
            model_size: "small", "medium", "large", "melody"
        """
        available = {
            "small": "facebook/musicgen-small",
            "medium": "facebook/musicgen-medium",
            "large": "facebook/musicgen-large",
            "melody": "facebook/musicgen-melody",
        }

        if model_size not in available:
            raise ValueError(f"Invalid model size: {model_size}")

        print(f"→ Loading MusicGen model: {available[model_size]}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"→ Using device: {self.device}")

        self.model = MusicGen.get_pretrained(available[model_size]).to(self.device)

    def generate(
        self,
        prompt: str,
        duration_seconds: int,
        bpm: int,
    ) -> np.ndarray:
        """
        Generate music from a text prompt.

        Returns:
            numpy array audio waveform
        """

        print(f"→ Generating music: {duration_seconds}s, {bpm} BPM")
        print("→ Prompt:", prompt)

        self.model.set_generation_params(
            use_sampling=True,
            top_k=250,
            duration=duration_seconds,
        )

        wav = self.model.generate(
            descriptions=[prompt],
            progress=True,
        )[0]  # shape: (channels, samples)

        return wav.cpu().numpy()