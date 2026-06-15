import os
import requests
from abc import ABC, abstractmethod

# =========================
# BASE
# =========================
class LLMInterface(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

# =========================
# DUMMY
# =========================
class DummyLLM(LLMInterface):
    def generate(self, prompt: str) -> str:
        return f"[DUMMY]\n{prompt}"

# =========================
# OLLAMA LOCAL
# =========================
class OllamaLocalAdapter(LLMInterface):
    def __init__(self, model="llama3", base_url="http://localhost:11434"):
        self.url = f"{base_url}/api/chat"
        self.model = model

    def generate(self, prompt: str) -> str:
        with requests.Session() as session:
            r = session.post(
                self.url,
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=120
            )
            r.raise_for_status()
            return r.json()["message"]["content"]

# =========================
# OLLAMA CLOUD (API KEY)
# =========================
class OllamaCloudAdapter(LLMInterface):
    def __init__(self, model, api_key, base_url):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        with requests.Session() as session:
            r = session.post(
                f"{self.base_url}/api/chat",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=120
            )
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                return f"[CLOUD ERROR] {data['error']}"
            return data["message"]["content"]

# =========================
# GOOGLE (REST API)
# =========================
class GoogleAdapter(LLMInterface):
    def __init__(self, model="gemini-2.0-flash"):
        self.model = model
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com"

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/v1beta/models/{self.model}:generateContent"
        with requests.Session() as session:
            r = session.post(
                url,
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ]
                },
                timeout=120
            )
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                return f"[GOOGLE ERROR] {data['error']['message']}"
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                return str(data)