import requests
import os

OLLAMA_HOST = os.environ.get('LLM_HOST', 'http://localhost')
OLLAMA_PORT = os.environ.get('LLM_PORT', '11434')
OLLAMA_MODEL = os.environ.get('LLM_MODEL', 'codellama')
OLLAMA_URL = f"{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"


def query_ollama(prompt, model=OLLAMA_MODEL):
    """Send a prompt to the Ollama server and return the response text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get('response', '').strip()
    except Exception as e:
        return f"[ERROR] Ollama LLM: {e}" 