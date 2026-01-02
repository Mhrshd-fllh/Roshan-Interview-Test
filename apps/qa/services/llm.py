from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from django.conf import settings
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
    
@dataclass
class HFConfig:
    model_name: str
    max_new_tokens: int
    temperature: float

_hf_lock = threading.Lock()
_hf_pipeline = None
_hf_model_name = None


class HuggingFaceLLM(BaseLLM):
    """
    Local LLM using HuggingFace transformers (CPU).
    Uses a cached pipeline so we don't reload the model on every request.
    """
    name = "hf"
    def __init__(self, cfg: HFConfig):
        self.cfg = cfg
        self._ensure_pipeline(cfg.model_name)
    
    def _ensure_pipeline(self, model_name: str):
        global _hf_pipeline, _hf_model_name

        with _hf_lock:
            if _hf_pipeline is not None and _hf_model_name == self.cfg.model_name:
                return
            from transformers import pipeline

            _hf_pipeline = pipeline(
                task = "text2text-generation",
                model = self.cfg.model_name,
                device = -1
            )
            _hf_model_name = model_name

    def generate(self, prompt: str) -> str:
        global _hf_pipeline

        if _hf_pipeline is None:
            raise LLMError("HF pipeline is not initialized")
        
        prompt = (prompt or "").strip()
        if not prompt:
            raise LLMError("Prompt is empty")
        
        out = _hf_pipeline(
            prompt,
            max_new_tokens = self.cfg.max_new_tokens,
            do_sample = self.cfg.temperature > 0.0,
            temperature = self.cfg.temperature,
        )

        text = (out[0]["generated_text"] or "").strip()
        return text or "I don't know based on the provided documents."


def get_llm() -> BaseLLM:
    provider = (os.getenv("LLM_PROVIDER") or getattr(settings, "LLM_PROVIDER", "stub")).lower()

    if provider == "stub":
        return StubLLM()

    if provider in ("hf", "huggingface", "transformers"):
        model_name = os.getenv("LLM_MODEL_NAME") or getattr(settings, "LLM_MODEL_NAME", "google/flan-t5-base")
        max_new_tokens = int(os.getenv("LLM_MAX_NEW_TOKENS") or getattr(settings, "LLM_MAX_NEW_TOKENS", 256))
        temperature = float(os.getenv("LLM_TEMPERATURE") or getattr(settings, "LLM_TEMPERATURE", 0.2))
        return HuggingFaceLLM(HFConfig(model_name=model_name, max_new_tokens=max_new_tokens, temperature=temperature))

    raise LLMError(f"Unsupported LLM_PROVIDER: {provider}")