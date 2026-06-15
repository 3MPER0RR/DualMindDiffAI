import time
import os
from llm import (
    DummyLLM,
    OllamaLocalAdapter,
    OllamaCloudAdapter,
    GoogleAdapter
)
from engines.raw import RawEngine
from engines.safe import SafeEngine
from core.loader import load_file
from core.diff import diff

# =========================
# FACTORY
# =========================
def build_llm(mode="dummy", model=None):
    mode = mode.lower()
    if mode == "dummy":
        return DummyLLM()
    if mode == "ollama-local":
        return OllamaLocalAdapter(model=model or "llama3")
    if mode == "ollama-cloud":
        return OllamaCloudAdapter(
            model=model or "gemma4:31b-cloud",
            api_key=os.getenv("OLLAMA_API_KEY"),
            base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com")
        )
    if mode == "google":
        return GoogleAdapter(model=model or "gemini-2.5-flash")
    return DummyLLM()

# =========================
# RUN
# =========================
def run(prompt, file_path=None, safe_llm_mode="dummy", safe_model=None, raw_llm_mode="dummy", raw_model=None):
    context = load_file(file_path) if file_path else ""

    # SAFE
    safe_llm = build_llm(safe_llm_mode, safe_model)
    safe_engine = SafeEngine(safe_llm)

    # RAW
    raw_llm = build_llm(raw_llm_mode, raw_model)
    raw_engine = RawEngine(raw_llm)

    safe_out = safe_engine.run(prompt, context)
    time.sleep(1.5)
    raw_out = raw_engine.run(prompt, context)

    print("\n=== SAFE ===\n")
    print(safe_out)
    print("\n=== RAW ===\n")
    print(raw_out)
    print("\n=== DIFF ===\n")
    print(diff(safe_out, raw_out))

# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run(
        prompt="Analyze the system architecture in the document.",
        file_path="data/sample.txt",
        safe_llm_mode="ollama-cloud",
        safe_model="gpt-oss:120b-cloud",
        raw_llm_mode="google",
        raw_model="gemini-2.5-flash"
    )