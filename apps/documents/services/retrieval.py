from __future__ import annotations

from dataclasses import dataclass
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from apps.documents.models import Document

@dataclass(frozen=True)
class RetrievalResult:
    document: Document
    score: float

def retrieve_top_k(query: str, k: int = 3) -> List[RetrievalResult]:
    """
    Returns top-k documents most relevant to the query based on cosine similarity of TF-IDF vectors.

    Notes:
    - Fast and simple baseline for phase 2.
    - Later we can replace TF-IDF with embeddings.
    """
    query = (query or "").strip()
    if not query:
        return []
    
    docs = list(Document.objects.all().only("id", "title", "content"))
    if not docs:
        return []
    
    corpus = [d.content for d in docs]

    vectorizer = TfidfVectorizer(stop_words=None, max_features=5000, ngram_range=(1, 2))

    doc_matrix = vectorizer.fit_transform(corpus)
    query_vec = vectorizer.transform([query])

    scores = cosine_similarity(query_vec, doc_matrix).flatten()

    ranked = sorted(((docs[i], float(scores[i])) for i in range(len(docs))), key = lambda x: x[1], reverse=True)[:k]

    return [RetrievalResult(document=d, score = s) for d, s in ranked]
