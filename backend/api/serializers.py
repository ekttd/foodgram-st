from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Cart, Favorite, IngredientAmount,
                            Recipe, Tag)
from rest_framework import serializers
from users.models import Follow
from .constants import (MIN_COOKING_TIME, MAX_COOKING_TIME,
                        MIN_INGREDIENT_AMOUNT, MAX_INGREDIENT_AMOUNT)
from rest_framework.exceptions import ValidationError
from recipes.models import Ingredient

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Пользователи [GET]"""

    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    avatar = serializers.SerializerMethodField(method_name='get_avatar')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class CustomUserPostSerializer(UserCreateSerializer):
    """Пользователи [POST]"""
    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'password')


class PasswordSerializer(serializers.Serializer):
    """Смена пароля."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль.')
        return value

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class RecipePartSerializer(serializers.ModelSerializer):
    """Рецепт для списка подписок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Подписки пользователя."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    avatar = serializers.ImageField(source='author.avatar', read_only=True)
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return obj.author.following.filter(user=request.user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        queryset = obj.author.recipes.all()
        recipes_limit = request.GET.get('recipes_limit')
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipePartSerializer(queryset, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class FollowToSerializer(serializers.ModelSerializer):
    """Подписаться/удалить подписку."""
    class Meta:
        model = Follow
        fields = (
            'user',
            'author'
        )

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Unable to follow yourself.'
            )
        if user.following.filter(author=author).exists():
            raise serializers.ValidationError(
                'Already followed.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = FollowSerializer(
            instance,
            context=context
        )
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Вывод тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )
        read_only_fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Ингридиенты."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit'
        )


class AddIngredientSerializer(serializers.ModelSerializer):
    """Добавление ингридиента в рецепт."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class IngredientAmountReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT,
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountWriteSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'image', 'name', 'text', 'cooking_time')

    def validate(self, data):
        ingredients = data.get('ingredients')
        request_method = self.context['request'].method
        if request_method in ['PUT', 'PATCH'] and ingredients is None:
            raise serializers.ValidationError({
                'ingredients': 'Это поле обязательно при обновлении.'
            })
        if ingredients:
            ingredient_ids = [item['id'] for item in ingredients]
            existing = Ingredient.objects.filter(id__in=ingredient_ids)
            if len(existing) != len(set(ingredient_ids)):
                raise serializers.ValidationError('Ингредиентов нет.')
        return data

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError("Image не может быть пустым.")
        return image

    def create_ingredients(self, ingredients, recipe):
        objs = []
        for ingredient in ingredients:
            objs.append(
                IngredientAmount(
                    recipe=recipe,
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount']
                )
            )
        IngredientAmount.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context
        ).data

    def update(self, instance, validated_data):

        ingredients = validated_data.pop('ingredients', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)

        return instance

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise ValidationError('Добавьте хотя бы один ингредиент.')

        ingredient_ids = [item['id'] for item in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError('Ингредиенты не должны повторяться.')

        existing_ids = set(
            Ingredient.objects.filter(id__in=ingredient_ids)
            .values_list('id', flat=True)
        )

        invalid_ids = [id for id in ingredient_ids if id not in existing_ids]
        if invalid_ids:
            raise ValidationError(f"Ингредиент(ы) с id {invalid_ids}"
                                  "не существует.")

        return ingredients


class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    ingredients = IngredientAmountReadSerializer(source='ingredient_in_recipe',
                                                 many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def is_exists_in(self, obj, model):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.is_exists_in(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.is_exists_in(obj, Cart)
