from __future__ import annotations

import time
from typing import Optional

from django.db import transaction

from apps.documents.services.retrieval import retrieve_top_k
from apps.qa.models import Answer, Question
from apps.qa.services.context import pack_context
from apps.qa.services.llm import get_llm, LLMError
from apps.qa.services.prompts import build_prompt, PROMPT_VERSION


def generate_answer_for_question(question_text: str, top_k: int, max_context_chars: int) -> Answer:
    """
    End-to-end pipeline:
      1) Create Question
      2) Retrieve top-k documents
      3) Pack context (bounded)
      4) Build prompt
      5) Call LLM
      6) Persist Answer + sources + metadata
    """

    started = time.perf_counter()

    with transaction.atomic():
        q = Question.objects.create(text=question_text)
        a = Answer.objects.create(question=q, status=Answer.Status.PENDING, retrieval_top_k=top_k, prompt_version = PROMPT_VERSION)

    results = retrieve_top_k(question_text, k=top_k)
    packed = pack_context(results, max_chars=max_context_chars)

    try:
        llm = get_llm()
        prompt = build_prompt(context=packed.text, question=question_text)
        text = llm.generate(prompt=prompt).strip()

        latency_ms = int((time.perf_counter() - started) * 1000)

        with transaction.atomic():
            a.text = text
            a.status = Answer.Status.SUCCESS
            a.model_name = getattr(llm, "name", "unknown")
            a.context_chars = packed.context_chars
            a.latency_ms = latency_ms
            a.error_message = ""
            a.save(update_fields=[
                "text", "status", "model_name", "context_chars", "latency_ms", "error_message"
            ])
            if packed.used_doc_ids:
                a.source_documents.set(packed.used_doc_ids)

        return a
    
    except Exception as e:
        latency_ms = int((time.perf_counter() - started) * 1000)

        with transaction.atomic():
            a.status = Answer.Status.FAILED
            a.error_message = str(e)
            a.latency_ms = latency_ms
            a.save(update_fields=["status", "error_message", "latency_ms"])
        return a