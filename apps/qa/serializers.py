from rest_framework import serializers


class RetrievalRequestSerializer(serializers.Serializer):
    question = serializers.CharField(help_text="User question")
    k = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        max_value=20,
        help_text="Number of documents to retrieve",
    )


class AskRequestSerializer(serializers.Serializer):
    question = serializers.CharField(help_text="User question")
    k = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        max_value=20,
        help_text="Number of documents to use for retrieval",
    )


class AskSourceSerializer(serializers.Serializer):
    rank = serializers.IntegerField(help_text="Rank of the retrieved document (1 is best)")
    document_id = serializers.IntegerField(help_text="ID of the source document")
    title = serializers.CharField(help_text="Title of the source document")
    score = serializers.FloatField(help_text="Similarity score between question and document")


class AskResponseSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(help_text="ID of the created question")
    answer_id = serializers.IntegerField(help_text="ID of the generated answer")
    status = serializers.CharField(help_text="Status of the answer generation")
    answer = serializers.CharField(allow_blank=True, help_text="Generated answer text")
    sources = AskSourceSerializer(many=True, help_text="Retrieved sources used for answering")
    model_name = serializers.CharField(allow_blank=True, help_text="Name of the LLM model used")    
    prompt_version = serializers.CharField(allow_blank=True, help_text="Version of the prompt template used")
    latency_ms = serializers.IntegerField(help_text="Latency in milliseconds for answer generation")
class RetrievalResultSerializer(serializers.Serializer):
    rank = serializers.IntegerField(help_text="Rank of the retrieved document (1 is best)")
    document_id = serializers.IntegerField(help_text="ID of the retrieved document")
    title = serializers.CharField(help_text="Title of the retrieved document")
    score = serializers.FloatField(help_text="Similarity score between question and document")


class RetrievalResponseSerializer(serializers.Serializer):
    question = serializers.CharField(help_text="The user question")
    k = serializers.IntegerField(help_text="Number of retrieved documents")
    results = RetrievalResultSerializer(many=True, help_text="Ranked retrieval results")
