from __future__ import annotations

import time
from django.db import transaction

from apps.qa.models import Answer, Question
from apps.qa.langchain.llm import get_langchain_llm
from apps.qa.langchain.chain import build_rag_chain


def generate_answer_for_question(question_text: str, top_k: int, max_context_chars: int) -> Answer:
    started = time.perf_counter()

    with transaction.atomic():
        q = Question.objects.create(text=question_text)
        a = Answer.objects.create(
            question=q,
            status=Answer.Status.PENDING,
            retrieval_top_k=top_k,
            prompt_version="langchain-v1",
        )

    try:
        llm = get_langchain_llm()
        chain = build_rag_chain(llm, k=top_k)

        # invoke expects dict with "input"
        out = chain.invoke(question_text)
        answer_text = (out.get("answer") or "").strip()
        ctx_docs = out.get("context") or []
        used_ids = []
        for d in ctx_docs:
            doc_id = d.metadata.get("document_id")
            if doc_id:
                used_ids.append(int(doc_id))

        latency_ms = int((time.perf_counter() - started) * 1000)

        with transaction.atomic():
            a.text = answer_text
            a.status = Answer.Status.SUCCESS
            a.model_name = getattr(llm, "model", "") or getattr(llm, "_llm_type", "") or "langchain"
            a.context_chars = min(max_context_chars, len("".join([d.page_content for d in ctx_docs])))
            a.latency_ms = latency_ms
            a.error_message = ""
            a.save(update_fields=["text", "status", "model_name", "context_chars", "latency_ms", "error_message"])

            if used_ids:
                a.source_documents.set(used_ids)

        return a

    except Exception as e:
        latency_ms = int((time.perf_counter() - started) * 1000)
        with transaction.atomic():
            a.status = Answer.Status.FAILED
            a.error_message = str(e)
            a.latency_ms = latency_ms
            a.save(update_fields=["status", "error_message", "latency_ms"])
        return a
