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
    k = serializers.IntegerField(required = False, default = 3, min_value = 1, max_value = 20)

class AskResponseSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(help_text="ID of the created question")
    answer_id = serializers.IntegerField(help_text="ID of the generated answer")
    status = serializers.CharField(help_text="Status of the answer generation")
    answer = serializers.CharField(allow_blank=True, help_text="Generated answer text")
    sources = serializers.ListField(child=serializers.IntegerField(), help_text="List of source document IDs")
    model_name = serializers.CharField(allow_blank=True, help_text="Name of the LLM model used")
    prompt_version = serializers.CharField(allow_blank=True, help_text="Version of the prompt template used")
    latency_ms = serializers.IntegerField(help_text="Latency in milliseconds for answer generation")