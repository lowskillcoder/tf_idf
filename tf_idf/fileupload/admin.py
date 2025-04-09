from django.contrib import admin
from .models import UploadedFile, WordStats

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at')
    ordering = ('-uploaded_at',)

def clear_document_count(modeladmin, request, queryset):
    """Сбрасывает счетчик документов для выбранных слов"""
    queryset.update(document_count=0)
clear_document_count.short_description = "Очистить статистику документов"

def delete_selected_stats(modeladmin, request, queryset):
    """Удаляет выбранные записи статистики слов"""
    queryset.delete()
delete_selected_stats.short_description = "Удалить статистику слов"

@admin.register(WordStats)
class WordStatsAdmin(admin.ModelAdmin):
    list_display = ('word', 'document_count')
    search_fields = ('word',)
    ordering = ('-document_count', 'word')
    actions = [clear_document_count, delete_selected_stats]
