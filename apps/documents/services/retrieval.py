from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import hashlib

from django.core.cache import cache
from django.db.models import Case, When

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from apps.documents.models import Document

_CACHE_TIMEOUT_SECONDS = 300

def _cache_key(query: str, k: int) -> str:
    q = query.strip().lower()
    h = hashlib.sha256(q.encode("utf-8")).hexdigest()
    return f"retrieve:tfidf:{h}:k={k}"

@dataclass(frozen=True)
class RetrievalResult:
    document: Document
    score: float

def retrieve_top_k(query: str, k: int = 3) -> List[RetrievalResult]:
    """
    Returns top-k documents most relevant to the query based on cosine similarity of TF-IDF vectors.

    Cache behavior:
    - Cache key: hash(query) + k
    - Cache value: List[(doc_id, score)]
    - TTL: 5 minutes
    """
    query = (query or "").strip()
    if not query:
        return []

    k = int(k or 3)
    if k < 1:
        return []

    # ---- Cache lookup ----
    key = _cache_key(query, k)
    cached: List[Tuple[int, float]] | None = cache.get(key)

    if cached:
        # Rehydrate documents while preserving order
        doc_ids = [doc_id for doc_id, _ in cached]

        preserved_order = Case(
            *[When(id=doc_id, then=pos) for pos, doc_id in enumerate(doc_ids)]
        )

        docs = list(
            Document.objects
            .filter(id__in=doc_ids)
            .only("id", "title", "content")
            .order_by(preserved_order)
        )

        doc_map = {d.id: d for d in docs}
        return [
            RetrievalResult(document=doc_map[doc_id], score=score)
            for doc_id, score in cached
            if doc_id in doc_map
        ]

    # ---- Cache miss: compute TF-IDF ----
    docs = list(Document.objects.all().only("id", "title", "content"))
    if not docs:
        return []

    corpus = [(d.content or "") for d in docs]

    vectorizer = TfidfVectorizer(
        stop_words=None,
        max_features=5000,
        ngram_range=(1, 2),
    )

    doc_matrix = vectorizer.fit_transform(corpus)
    query_vec = vectorizer.transform([query])

    scores = cosine_similarity(query_vec, doc_matrix).flatten()

    ranked = sorted(
        ((docs[i], float(scores[i])) for i in range(len(docs))),
        key=lambda x: x[1],
        reverse=True,
    )[:k]

    results = [RetrievalResult(document=d, score=s) for d, s in ranked]

    # ---- Save cache (primitive only) ----
    cache_payload = [(r.document.id, float(r.score)) for r in results]
    cache.set(key, cache_payload, timeout=_CACHE_TIMEOUT_SECONDS)

    return results
