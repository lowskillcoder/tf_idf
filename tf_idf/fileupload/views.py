from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import UploadedFile, WordStats
from .utils import process_file
import os
import shutil

def upload_page(request):
    """
    Простое представление для отображения страницы загрузки файла.
    """
    return render(request, 'fileupload/upload.html')

@csrf_exempt
def clear_database(request):
    """
    Очистка базы данных и папки с загруженными файлами.
    """
    if request.method == 'POST':
        # Удаляем все записи о словах
        WordStats.objects.all().delete()
        
        # Удаляем все загруженные файлы из базы данных
        UploadedFile.objects.all().delete()
        
        # Очищаем папку media/uploads
        media_dir = os.path.join('media', 'uploads')
        if os.path.exists(media_dir):
            for file in os.listdir(media_dir):
                file_path = os.path.join(media_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Ошибка при удалении {file_path}: {e}")
        
        return JsonResponse({'status': 'success', 'message': 'База данных и файлы успешно очищены'})
    
    return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'}, status=405)

class FileUploadView(APIView):
    """
    API для загрузки файлов и обработки TF-IDF.
    """
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({'error': 'Файл не найден'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Отладочная информация
        print(f"Получен файл: {file_obj.name}, размер: {file_obj.size} байт")
        
        # Сохраняем файл
        instance = UploadedFile(file=file_obj)
        instance.save()
        
        # Отладочная информация о сохраненном файле
        print(f"Файл сохранен как: {instance.file.path}")
        
        # Обрабатываем файл
        try:
            result = process_file(instance.file.path)
            
            # Отладка: подсчитываем общее количество документов после обработки
            doc_count = UploadedFile.objects.count()
            print(f"После обработки, общее количество документов: {doc_count}")
            
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Ошибка при обработке файла: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
