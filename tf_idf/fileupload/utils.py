import re
import math
import os
from collections import Counter
from .models import WordStats, UploadedFile

def process_file(file_path):
    """
    Обрабатывает текстовый файл и вычисляет TF-IDF для слов с учетом истории загрузок.
    
    Args:
        file_path: Путь к файлу для обработки
        
    Returns:
        Список словарей с информацией о 50 словах с наибольшим IDF
    """
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read().lower()
    except UnicodeDecodeError:
        # Если возникла ошибка с UTF-8, попробуем другую кодировку
        with open(file_path, 'r', encoding='cp1251') as f:
            text = f.read().lower()
    
    # Очистка текста от знаков препинания и разделение на слова
    words = re.findall(r'\b\w+\b', text)
    
    # Подсчет TF (частота термина)
    word_count = Counter(words)
    total_words = len(words)
    
    # Обновляем статистику по словам в базе данных
    # Для каждого уникального слова в документе увеличиваем счетчик документов
    unique_words = set(word for word in words if len(word) > 1)
    
    for word in unique_words:
        word_stat, created = WordStats.objects.get_or_create(word=word)
        if created:
            word_stat.document_count = 1
        else:
            word_stat.document_count += 1
        word_stat.save()
    
    # Получаем общее количество документов
    # Используем количество загруженных файлов как количество документов
    total_documents = UploadedFile.objects.count()
    
    # Вычисляем TF-IDF
    tf_idf_data = []
    
    for word, count in word_count.items():
        if len(word) > 1:  # Игнорируем однобуквенные слова
            # TF - относительная частота слова (количество вхождений слова / общее количество слов)
            tf = count / total_words
            
            # Получаем количество документов, содержащих данное слово
            try:
                word_stat = WordStats.objects.get(word=word)
                doc_count = word_stat.document_count
            except WordStats.DoesNotExist:
                doc_count = 1  # Если статистики нет, предполагаем, что слово встречается в 1 документе
            
            # IDF - используем формулу: idf(t) = log(N / (1 + df(t))), где:
            # N - общее количество документов
            # df(t) - количество документов, содержащих термин t
            
            # Проверка: избегаем деления на ноль и отрицательного логарифма
            denominator = 1 + doc_count
            if total_documents >= denominator:
                idf = math.log10(total_documents / denominator)
            else:
                idf = 0
            
            tf_idf_data.append({
                'word': word,
                'tf': tf,
                'idf': idf,
                'count': count,
                'doc_count': doc_count,
            })
    
    # Сортировка по убыванию IDF
    tf_idf_data.sort(key=lambda x: x['idf'], reverse=True)
    
    # Возвращаем первые 50 слов
    return tf_idf_data[:50] 