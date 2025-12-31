from django.contrib import admin
from .models import Question, Answer

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ['id', 'short_text', 'created_at']
    ordering = ['-created_at']

    def short_text(self, obj: Question) -> str:
        return (obj.text[:75] + '...') if len(obj.text) > 75 else obj.text
    
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    search_fields = ['text', 'question__text']
    list_display = ['id', 'question_id', 'short_text', 'created_at']
    autocomplete_fields = ['question']
    filter_horizontal = ['source_documents']

    def short_text(self, obj: Answer) -> str:
        return (obj.text[:75] + '...') if len(obj.text) > 75 else obj.text

