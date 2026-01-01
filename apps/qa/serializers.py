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