from __future__ import annotations

import os
from langchain_core.language_models import BaseLLM
from langchain_core.runnables import RunnableLambda

from django.conf import settings


def get_langchain_llm():
    provider = (os.getenv("LLM_PROVIDER") or getattr(settings, "LLM_PROVIDER", "stub")).lower()

    if provider == "stub":
        # Simple runnable that always refuses to hallucinate
        return RunnableLambda(lambda prompt: "I don't know based on the provided documents.")

    if provider in ("hf", "huggingface", "transformers"):
        from transformers import pipeline
        from langchain_community.llms import HuggingFacePipeline

        model_name = os.getenv("LLM_MODEL_NAME") or getattr(settings, "LLM_MODEL_NAME", "google/flan-t5-small")
        max_new_tokens = int(os.getenv("LLM_MAX_NEW_TOKENS") or getattr(settings, "LLM_MAX_NEW_TOKENS", 128))
        temperature = float(os.getenv("LLM_TEMPERATURE") or getattr(settings, "LLM_TEMPERATURE", 0.2))

        hf = pipeline(
            "text2text-generation",
            model=model_name,
            device=-1,
        )

        llm = HuggingFacePipeline(
            pipeline=hf,
            model_kwargs={
                "max_new_tokens": max_new_tokens,
                "do_sample": temperature > 0,
                "temperature": temperature,
            },
        )
        return llm

    raise RuntimeError(f"Unsupported LLM_PROVIDER for LangChain: {provider}")
