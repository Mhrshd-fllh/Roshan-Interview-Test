from django.db import models
from apps.documents.models import Document


class Question(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Q#{self.id}"
    

class Answer(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    source_documents = models.ManyToManyField(Document, related_name='answers', blank=True)
    

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True, null=True)

    model_name = models.CharField(max_length=128, blank = True)
    prompt_version = models.CharField(max_length = 32, blank = True)

    retrieval_top_k = models.PositiveSmallIntegerField(default=3)
    context_chars = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"A#{self.id} for Q#{self.question.id} [{self.status}]"
