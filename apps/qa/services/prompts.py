PROMPT_VERSION = "v1"

SYSTEM_STYLE = """You are a helpful assistant.
Answer strictly using the provided context.
If the context does not contain enough information, say: "I don't know based on the provided documents."
Include citations like [D1], [D2] for claims you make.
Keep the answer concise and accurate.
"""


def build_prompt(context: str, question: str) -> str:
    return f"""{SYSTEM_STYLE}
    
    Question:
    {question}

    Context:
    {context}
    
    Answer:
    """

