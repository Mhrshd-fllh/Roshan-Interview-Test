PROMPT_VERSION = "v1"

SYSTEM_STYLE = """You are a helpful assistant.
You MUST answer using only the provided context.
If the context is insufficient, say exactly: "I don't know based on the provided documents."
Cite sources using [D1], [D2] for each factual claim.
Do not invent details not present in the context.
"""


def build_prompt(context: str, question: str) -> str:
    return f"""{SYSTEM_STYLE}
    
    Question:
    {question}

    Context:
    {context}
    
    Answer:
    """

