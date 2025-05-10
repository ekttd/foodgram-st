# foodgram/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Обработчик запроса на /ping
def ping_view(request):
    return JsonResponse({'message': 'pong'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipes.urls')),
]
