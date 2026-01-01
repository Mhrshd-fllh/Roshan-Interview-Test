import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.documents.services.retrieval import retrieve_top_k

@require_POST
def retrieve_view(request):
    payload = json.loads(request.body.decode("utf-8") or "{}")
    question = (payload.get("question") or "").strip()
    k = int(payload.get("k") or 3)

    results = retrieve_top_k(question, k=k)
    return JsonResponse({"question": question, "k": k, "results": [{"document_id": r.document.id,"title": r.document.title, "score": r.score} for r in results],})
