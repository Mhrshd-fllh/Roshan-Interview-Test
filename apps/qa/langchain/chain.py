from __future__ import annotations

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap, RunnablePassthrough, RunnableLambda

from apps.qa.langchain.retriever import TfidfDBRetriever


def _format_docs(docs) -> str:
    parts = []
    for i, d in enumerate(docs, start=1):
        title = d.metadata.get("title", "")
        parts.append(f"[D{i}] {title}\n{d.page_content}")
    return "\n\n".join(parts)


def build_rag_chain(llm, *, k: int = 3):
    """
    Returns a LangChain Runnable (LCEL) with `.invoke(question: str)` support.

    Output:
      {"answer": str, "context": list[langchain_core.documents.Document]}
    """
    retriever = TfidfDBRetriever(k=k)

    prompt = PromptTemplate.from_template(
        """You are a helpful assistant.
You MUST answer using only the provided context.
If the context is insufficient, say exactly: "I don't know based on the provided documents."
Cite sources using [D1], [D2], ... for each factual claim.

Question:
{question}

Context:
{context}

Answer:
"""
    )

    base = RunnableMap(
        {
            "question": RunnablePassthrough(),
            "context_docs": retriever,
        }
    )

    add_context = RunnableMap(
        {
            "question": RunnableLambda(lambda x: x["question"]),
            "context_docs": RunnableLambda(lambda x: x["context_docs"]),
            "context": RunnableLambda(lambda x: _format_docs(x["context_docs"])),
        }
    )

    final = RunnableMap(
        {
            "answer": prompt | llm | StrOutputParser(),
            "context": RunnableLambda(lambda x: x["context_docs"]),
        }
    )

    return base | add_context | final
