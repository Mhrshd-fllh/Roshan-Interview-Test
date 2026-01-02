from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from apps.documents.services.retrieval import retrieve_top_k
from .serializers import RetrievalRequestSerializer

from apps.qa.serializers import AskRequestSerializer, AskResponseSerializer
from apps.qa.services.answer_generation import generate_answer_for_question
from django.conf import settings

class RetrieveAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RetrievalRequestSerializer

    @extend_schema(
            request = RetrievalRequestSerializer,
            responses = {200: dict},
            description = "Retrieve top-k relevant documents for a given question",
    )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        k = serializer.validated_data["k"]

        results = retrieve_top_k(question, k=k)

        return Response({
            "question": question,
            "k": k,
            "results": [
                {
                    "document_id": r.document.id,
                    "title": r.document.title,
                    "score": r.score,
                }
                for r in results
            ],
        })
    

class AskAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AskRequestSerializer

    @extend_schema(
        request = AskRequestSerializer,
        responses = {200: AskResponseSerializer},
        description = "Ask a question. The system retrieves relevant documents and generates an answer using an LLM.",
    )
    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        question = s.validated_data["question"]
        k = s.validated_data["k"]

        top_k = int(getattr(settings, "RETRIEVAL_TOP_K", k) or k)
        max_chars = int(getattr(settings, "MAX_CONTEXT_CHARS", 1500))

        ans = generate_answer_for_question(question, top_k=top_k, max_context_chars=max_chars)

        return Response({
            "question_id": ans.question.id,
            "answer_id": ans.id,
            "status": ans.status,
            "answer": ans.text,
            "sources": list(ans.source_documents.values_list("id", flat=True)),
            "model_name": ans.model_name,
            "prompt_version": ans.prompt_version,
            "latency_ms": ans.latency_ms
        })

