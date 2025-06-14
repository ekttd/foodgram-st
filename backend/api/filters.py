from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    """
    Фильтр по выбранному автору, комбинации тегов,
    в избранном, в корзине.
    """
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset.exclude(favorited_by__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(carts__user=self.request.user)
        return queryset.exclude(carts__user=self.request.user)
