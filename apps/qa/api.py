from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from apps.documents.services.retrieval import retrieve_top_k
from .serializers import RetrievalRequestSerializer


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