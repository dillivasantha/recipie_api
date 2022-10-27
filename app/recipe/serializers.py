""""
serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe, Tag

class TagSerialzer(serializers.ModelSerializer):
    """ Serializer for tags ."""
    class Meta:
        model = Tag
        fields = ['id','name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerialzer(many=True, required=False) # by default this nested serializer is read only , add custom code below create()

    class Meta:
        model = Recipe
        fields = ['id','title','description','link','time_minutes','price','tags']
        read_only_fields = ['id']
    
    def _get_or_create_tags(self,tags, recipe):
        """handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            # get_or_create get tag if ecists if not it creates 
            tag_obj,created = Tag.objects.get_or_create(
                user=auth_user,
                **tag # in future if they pass more  than name or else name = tag['name']
            )
            recipe.tags.add(tag_obj)


    def create(self, validated_data):
        """Create a Recipe"""
        tags = validated_data.pop('tags',[])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user # to get user in serialzer use context , but in views u can get self.user
        self._get_or_create_tags(tags,recipe)
        return recipe
        #summary:1.remove sent tags 2. create recipe with out tags 
        # 3. create or get tags with that method and passing tags data which popped from validated data
        # 4. add tags to recipe finally 
        # 5 return complete recipe
     
    def update(self,instance,validated_data):
        """update recipe."""
        tags = validated_data.pop('tags',None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer): # as this is a extension for RecipeSerializer so using above and adding extra fields
    """Serializer for recipe details """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


