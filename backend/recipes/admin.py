from django.contrib import admin
from django.contrib.admin import ModelAdmin, register


from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            Cart, Tag)
from users.models import Follow


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name",)


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    min_num = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ("pk", "name", "author", "get_favorites", "pub_date")
    list_filter = ("author", "name")
    search_fields = ("name", "author__username")
    inlines = [IngredientAmountInline]

    @admin.display(description="Количество добавлений рецепта в избранное")
    def get_favorites(self, obj):
        return obj.favorites.count()


@register(IngredientAmount)
class IngredientInRecipe(ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")


@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ("pk", "user", "recipe")


@register(Follow)
class FollowAdmin(ModelAdmin):
    list_display = ("pk", "user", "author")
    search_fields = ("user__username", "author__username")
    list_filter = ("user", "author")


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ("pk", "user", "recipe")


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("pk", "name", "color", "slug")
    search_fields = ("name", "slug")
    list_filter = ("name",)
