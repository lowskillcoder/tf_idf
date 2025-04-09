from django.db import models

# Create your models here.

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"File {self.id} uploaded at {self.uploaded_at}"

class WordStats(models.Model):
    """Модель для хранения статистики слов в документах"""
    word = models.CharField(max_length=100, unique=True)
    document_count = models.IntegerField(default=0)  # Количество документов, содержащих слово
    
    def __str__(self):
        return f"{self.word} (in {self.document_count} documents)"
