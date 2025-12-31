from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name
    

class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='documents', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title