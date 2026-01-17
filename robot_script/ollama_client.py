"""
Ollama Client
=============
Simple HTTP client for calling Ollama locally.

Ollama must be installed and running:
- Download: https://ollama.com/download
- Start: `ollama serve`
- Pull model: `ollama pull phi3`
"""

import requests
import time


class OllamaClient:
    """
    Client for communicating with local Ollama instance.
    """
    
    def __init__(self, model="phi3", base_url="http://localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            model: Model name (e.g., "phi3", "llama3.1", "mistral")
            base_url: Base URL of Ollama API (default: localhost)
        """
        self.model = model
        self.base_url = base_url
        self.generate_url = f"{base_url}/api/generate"
    
    def is_running(self) -> bool:
        """
        Check if Ollama is running and accessible.
        
        Returns:
            True if Ollama is running, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def generate(self, prompt: str, temperature=0.7, max_retries=3) -> str:
        """
        Send a prompt to Ollama and get response.
        
        Args:
            prompt: The prompt text to send
            temperature: Creativity (0.0=deterministic, 1.0=creative)
            max_retries: Number of retry attempts on failure
        
        Returns:
            Generated text response
        
        Raises:
            ConnectionError: If Ollama is not accessible
            RuntimeError: If generation fails after retries
        """
        if not self.is_running():
            raise ConnectionError(
                "Ollama is not running. Please start it:\n"
                "  1. Install: https://ollama.com/download\n"
                "  2. Start: ollama serve\n"
                "  3. Pull model: ollama pull " + self.model
            )
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.generate_url,
                    json=payload,
                    timeout=120  # Ollama can be slow on CPU, especially first load
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("response", "").strip()
                
            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                if attempt < max_retries - 1:
                    print(f"  ⚠ Timeout on attempt {attempt + 1}, retrying...")
                    time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    print(f"  ⚠ Error on attempt {attempt + 1}, retrying...")
                    time.sleep(2)
        
        raise RuntimeError(f"Failed to generate after {max_retries} attempts: {last_error}")
