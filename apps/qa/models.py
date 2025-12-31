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
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    text = models.TextField() # Empty for now
    created_at = models.DateTimeField(auto_now_add=True)

    source_documents = models.ManyToManyField(Document, related_name='answers', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"A#{self.id} for Q#{self.question.id}"

