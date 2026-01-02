from __future__ import annotations

from dataclasses import dataclass

from typing import List, Tuple

from apps.documents.services.retrieval import RetrievalResult

@dataclass(frozen=True)
class PackedContext:
    text: str
    used_doc_ids: List[int]
    context_chars: int

def pack_context(results: List[RetrievalResult], max_chars: int) -> PackedContext:
    """
    Packs retrieved documents into a single context string with simple citations.
    Ensures we never exceed max_chars (rough guardrail to control prompt size).
    """
    chunks: List[str] = []
    used_doc_ids: List[int] = []
    total = 0

    for idx, r in enumerate(results):
        doc = r.document
        header = f"[D{idx}] {doc.title}\n"
        body = (doc.content or "").strip()
        piece = header + body + "\n"

        if total + len(piece) > max_chars:
            remaining = max_chars - total
            if remaining <= 0:
                break
            piece = piece[:remaining]
        chunks.append(piece)

        used_doc_ids.append(doc.id)
        total += len(piece)

        if total >= max_chars:
            break

    ctx = "\n---\n".join(chunks).strip()
    return PackedContext(text=ctx, used_doc_ids=used_doc_ids, context_chars=len(ctx))