class RawEngine:
    def __init__(self, llm):
        self.llm = llm

    def run(self, prompt, context=""):
        full_prompt = f"""
You are a reasoning engine.

Context:
{context}

Task:
{prompt}
"""
        return self.llm.generate(full_prompt)
