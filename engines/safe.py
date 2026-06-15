class SafeEngine:
    def __init__(self, llm):
        self.llm = llm

    def sanitize(self, text: str) -> str:
        blacklist = ["step", "exploit", "bypass", "payload"]
        for w in blacklist:
            text = text.replace(w, "[filtered]")
        return text

    def run(self, prompt, context=""):
        full_prompt = f"""
You are a safe reasoning engine.

Context:
{context}

Task:
{prompt}
"""

        out = self.llm.generate(full_prompt)
        return self.sanitize(out)
