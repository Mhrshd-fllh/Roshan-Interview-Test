from __future__ import annotations

import os

class LLMError(RuntimeError):
    pass


class BaseLLM:
    name: str = "base"

    def generate(self, prompt: str) -> str:
        raise NotImplementedError
    

class StubLLM(BaseLLM):
    """
    Safe fallback: produces a determenistic, context-grounded style output.
    Good for ensuring the whole pipeline works end-to-end.
    """

    name = "stub"

    def generate(self, prompt: str) -> str:
        return "I don't know based on the provided documents."
    

def get_llm() -> BaseLLM:
    provider = (os.getenv("LLM_PROVIDER") or "stub").lower()

    if provider == "stub":
        return StubLLM()
    
    raise LLMError(f"Unsupported LLM provider: {provider}")