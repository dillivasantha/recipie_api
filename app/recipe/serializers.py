""""
serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    class Meta:
        model = Recipe
        fields = ['id','title','description','link','time_minutes','price']
        read_only_fields = ['id']

class RecipeDetailSerializer(RecipeSerializer): # as this is a extension for RecipeSerializer so using above and adding extra fields
    """Serializer for recipe details """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
