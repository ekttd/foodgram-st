# views.py
from rest_framework import viewsets
from .models import Recipe
from django.shortcuts import render


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-created_at')


def main_page(request):
    recipes = Recipe.objects.all().order_by('-created_at')[:6]
    return render(request, 'src/pages/main/index.js', {'recipes': recipes})
