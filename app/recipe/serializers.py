from rest_framework import serializers
from core.models import (
    Recipe,
    Tag,
    Ingredient
)

class TagSerializer(serializers.ModelSerializer):
    """serializer a tag"""

    class Meta:
        model = Tag
        fields = [
            'id', 'name'
        ]
        read_on_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    """serializer a ingredient"""

    class Meta:
        model = Tag
        fields = [
            'id', 'name'
        ]
        read_on_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Serialize a recipe"""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients'
        ]
        read_only_fields = ('id',)

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredient(self, ingredients, recipe):
        """Handle getting or creating ingredient as needed"""
        auth_user = self.context.get('request').user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user = auth_user,
                **ingredient
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validate_data):
        """Create recipe."""
        tags = validate_data.pop('tags', [])
        ingredients = validate_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validate_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredient(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredient(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detial view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading image to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}