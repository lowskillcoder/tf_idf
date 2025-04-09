from django.urls import path
from .views import upload_page, FileUploadView, clear_database

urlpatterns = [
    path('', upload_page, name='upload_page'),
    path('api/upload/', FileUploadView.as_view(), name='file_upload_api'),
    path('api/clear-db/', clear_database, name='clear_database'),
] 