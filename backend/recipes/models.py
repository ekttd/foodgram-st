from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from api.constants import MIN_COOKING_TIME, MAX_COOKING_TIME
User = get_user_model()


class Tag(models.Model):
    """Тег"""

    name = models.CharField(
        verbose_name='Название тэга',
        max_length=16,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цветовой HEX код',
        max_length=16,
        unique=True,
        validators=[RegexValidator(r'^#(?:[0-9a-fA-F]{3}){1,2}$')]
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} (цвет: {self.color})'


class Ingredient(models.Model):
    """Ингридиент"""

    name = models.CharField(
        verbose_name='Название',
        max_length=150,
        db_index=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=10
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Рецепт"""

    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='food/',
        null=False,
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=3000
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientAmount",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
        )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'


class IngredientAmount(models.Model):
    """Many-to-many рецепт-ингридиенты с количеством"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes_with_ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )

    class Meta:
        verbose_name = 'Ингридиент с количеством'
        verbose_name_plural = 'Ингридиенты с количеством'
        ordering = ('ingredient__name',)

    def __str__(self):
        return f'{self.amount} {self.ingredient.name}'


class Favorite(models.Model):
    """Избранное"""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'Рецепт в списке избранного'
        verbose_name_plural = 'Рецепты в списке избранного'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='already in favorite')]

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Cart(models.Model):
    """Список покупок"""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='carts',
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='carts',
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='already in cart')]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
