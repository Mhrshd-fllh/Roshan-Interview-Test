from __future__ import annotations

from typing import List

from langchain_core.documents import Document as LCDocument
from langchain_core.retrievers import BaseRetriever

from apps.documents.services.retrieval import retrieve_top_k

class TfidfDBRetriever(BaseRetriever):
    """
    LangChain Retriever Wrapper around our existing TF-IDF retrieve_top_k().
    It returns LangChain Documents with metadata for citations.
    """

    k: int = 3
    def _get_relevant_documents(self, query):
        results = retrieve_top_k(query, k = self.k)

        docs = []
        for idx, r in enumerate(results, start= 1):
            d = r.document
            docs.append(
                LCDocument(
                    page_content=(d.content or ""),
                    metadata={
                        "document_id": d.id,
                        "title": d.title,
                        "score": float(r.score),
                        "rank": idx,
                    },
                )
            )
        return docs
        
