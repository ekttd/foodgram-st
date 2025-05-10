# views.py
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import Recipe
from .serializers import RecipeSerializer
from django.shortcuts import render


class RecipePagination(PageNumberPagination):
    page_size = 6  
    page_size_query_param = 'page_size'
    max_page_size = 100  

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination 

def main_page(request):
    recipes = Recipe.objects.all().order_by('-created_at')[:6]
    return render(request, 'src/pages/main/index.js', {'recipes': recipes})
