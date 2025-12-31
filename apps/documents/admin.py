from django.contrib import admin
from .models import Document, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']
    ordering = ['name']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['title', 'content']
    list_display = ['id', 'title', 'created_at']
    list_filter = ['created_at', 'tags']
    autocomplete_fields = ['tags']
    ordering = ['-created_at']

    

