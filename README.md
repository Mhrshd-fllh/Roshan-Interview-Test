# Roshan Interview Test — Document Question Answering (Doc-QA)


## Overview
This project is a backend service for question answering over a collection of documents.
It is implemented using Django and PostgreSQL, and uses a Retrieval-Augmented Generation (RAG)
pipeline built with LangChain.

Given a user question, the system retrieves the most relevant documents, constructs a context,
and generates an answer using a Large Language Model (LLM), while exposing clear citations
for the retrieved sources.

The service is exposed as a REST API and includes interactive Swagger (OpenAPI) documentation.

## Key Goals of the project

- Demonstrate clean Django backend architecture
- Implement document retrieval and question answering
- Integrate LangChain in a controlled and production-friendly way
- Provide clear, well-documented APIs
- Support Docker-based execution for easy setup and evaluation

## Features

- RESTful API built with Django Rest Framework
- Document retrieval using TF-IDF and cosine similarity
- Retrieval-Augmented Generation (RAG) pipeline
- LangChain-based orchestration (Retriever, Prompt, Chain)
- Support for multiple LLM providers (stub and HuggingFace)
- Precise source citations with rank and similarity score
- PostgreSQL database for persistence
- Docker and Docker Compose support
- Interactive Swagger / OpenAPI documentation

## What the system does
1. Accepts a user question through an API endpoint
2. Retrieves the top-k most relevant documents
3. Builds a context from retrieved documents
4. Generates an answer using an LLM
5. Returns the answer along with structured citations

## High-Level Flow
```
User Question
    ↓
Document Retrieval (TF-IDF + cosine similarity)
    ↓
LangChain RAG Pipeline
    - Context construction
    - Prompt template
    - LLM invocation
    ↓
Answer generation
    ↓
Persist answer and sources
    ↓
API response

```

## Django Application Structure

```
apps/
├── documents/
│   ├── models.py        # Document model
│   └── services/
│       └── retrieval.py # TF-IDF retrieval logic
│
├── qa/
│   ├── models.py        # Question and Answer models
│   ├── api.py           # REST API views
│   ├── serializers.py   # Request/response schemas
│   ├── services/
│   │   └── answer_generation.py
│   └── langchain/
│       ├── retriever.py # LangChain Retriever wrapper
│       ├── chain.py     # RAG chain (LCEL)
│       └── llm.py       # LLM configuration

```

## Separation of Concerns

- documents app:
  Responsible for storing documents and retrieving relevant content.

- qa app:
  Responsible for question answering logic, LangChain integration,
  persistence of questions/answers, and API exposure.

- services layer:
  Contains business logic, kept separate from views and serializers.

- langchain module:
  Encapsulates all LangChain-related code to avoid coupling it
  directly to Django views or models.

## Why this architecture

- Keeps retrieval, generation, and API concerns separated
- Makes it easy to replace TF-IDF with embeddings later
- Allows swapping LLM providers without changing API code
- Keeps LangChain usage explicit and testable

## How LangChain is used in this project

LangChain is used as the orchestration layer for the Retrieval-Augmented
Generation (RAG) pipeline.

Instead of relying on high-level, opaque abstractions, the project uses
LangChain's core building blocks to keep the pipeline explicit,
debuggable, and production-friendly.

## Implemented LangChain components

- Custom Retriever:
  A LangChain-compatible retriever wraps the existing TF-IDF retrieval
  logic and returns LangChain Document objects with metadata.

- PromptTemplate:
  A structured prompt enforces that answers are grounded in the provided
  context and explicitly requires source citations.

- LCEL (LangChain Expression Language):
  The RAG pipeline is built using RunnableMap, RunnableLambda, and
  RunnablePassthrough, allowing fine-grained control over each step.

- Output parsing:
  The final output is parsed as plain text while preserving access to
  the retrieved documents for citation purposes.

## Why IECL instead of high-level LangChain chains
High-level LangChain chains (e.g. RetrievalQA) abstract away too much
control for this use case.

Using LCEL provides:
- Explicit data flow between steps
- Clear separation between retrieval and generation
- Easier debugging and logging
- Better alignment with production backend requirements

## Citations and source taking

Each retrieved document is assigned a rank and similarity score.
This metadata is preserved throughout the LangChain pipeline and
returned in the API response as structured citations.

This makes the system explainable and avoids hallucinated answers.

## Required environment variables 
### Django
```python
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=1

```

```python
DJANGO_DB_NAME=docqa
DJANGO_DB_USER=docqa
DJANGO_DB_PASSWORD=changeme
DJANGO_DB_HOST=db
DJANGO_DB_PORT=5432
```

### LLM configuration

```python
LLM_PROVIDER=stub
LLM_MODEL_NAME=google/flan-t5-small
```
## Running The Project

### Run with Docker
```bash
    docker compose up --build
```
After that API is available at:
```
http://localhost:8080
```

And Swagger:
```
http://localhost:8080/api/docs
```
Stopping Containers:
```bash
docker compose down
```
### Run Locally

```bash
python -m venv .venv
```
environment activation:
MacOS/Linux:
```bash
source .venv/bin/activate
```

Windows:
```bash
.venv\Scripts\activate
```
Installing dependencies:
```bash
.venv\Scripts\activate
```

Migration:
```bash
python manage.py migrate
```

Server run:
```bash
python manage.py runserver
```
##  API Endpoints and Usage

### 1) Retrieve top-k documents
Endpoint:
```
POST /api/retrieve
```
Request body:
```json
{
  "question": "What is Django ORM?",
  "k": 3
}
```

Response example:
```json
{
  "question": "What is Django ORM?",
  "k": 3,
  "results": [
    {
      "rank": 1,
      "document_id": 5,
      "title": "Django ORM Basics",
      "score": 0.73
    },
    {
      "rank": 2,
      "document_id": 2,
      "title": "Models and Queries",
      "score": 0.61
    }
  ]
}
```
Notes:
- score calculates based on cosine similarity of TF-IDF vectors
- rank shows the order of results.

### 2) Ask a Question (RAG)

Endpoint:
```
POST /api/qa/ask
```

Request body:
```json
{
  "question": "What is Django ORM?",
  "k": 3
}
```
Response example:
```json
{
  "question_id": 12,
  "answer_id": 12,
  "status": "success",
  "answer": "Django ORM is an abstraction layer for database access in Django [D1].",
  "sources": [
    {
      "rank": 1,
      "document_id": 5,
      "title": "Django ORM Basics",
      "score": 0.73
    }
  ],
  "model_name": "langchain",
  "prompt_version": "langchain-v1",
  "latency_ms": 4100
}
```
Notes:
- Answer generates by LangChain RAG Pipeline
- sources contains structured citations (rank/score/title)
- [D1], [D2], ... in answer text refers to sources

## Final status and next steps

### Current project status
- Core functionality implemented and working
- Document retrieval implemented using TF-IDF
- LangChain RAG pipeline integrated and stable
- PostgreSQL database configured
- Dockerized setup verified
- Swagger / OpenAPI documentation available
- Codebase structured for clarity and extensibility

### Design decisions
- TF-IDF was chosen as a simple and fast baseline for retrieval
- LangChain was used explicitly for orchestration, not as a black box
- LCEL was preferred over high-level chains for better control
- Django apps are separated by responsibility

### Possible next steps
- Replace TF-IDF with embedding-based retrieval
- Integrate a vector database (e.g. FAISS, pgvector)
- Add background processing for LLM calls (Celery / RQ)
- Add automated evaluation for answer quality
- Add authentication and rate limiting
- Improve prompt tuning and citation alignment

### Project scope note
This project focuses on correctness, clarity, and extensibility
rather than maximum model performance.

It is designed to be easy to review, reason about, and extend.

### Final Note
This project focuses on correctness, clarity, and extensibility
rather than maximum model performance.

It is designed to be easy to review, reason about, and extend.


