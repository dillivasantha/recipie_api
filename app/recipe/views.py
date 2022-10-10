"""
Views for the recipe APIs
"""
from rest_framework import viewsets
from recipe import serializers
from core.models import Recipe
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage REcipe APIs
    """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # till above it returns all recipes 
    # but to get user specific recipes filter by user as below get_queryset() method
    def get_queryset(self):
        """ Retrieve recipe for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    # most of times we use Detailserializer hence we implement this condition based method get_serializer_class and change above 
    #serializer_class = serializers.RecipeSerializer --->
    # serializer_class = serializers.RecipeDetailSerializer
    def get_serializer_class(self):
        """ Return the serializer class based on request action"""
        if self.action == 'list':
            return serializers.RecipeSerializer # we are returing just refferrence to class so no ()brackets used 
            # note - Django rest frame work will apply instance creation and work accordingly 
        # for all updating creating we use this RecipeDetailSerializer, Hence sepearted the list view  above , which uses RecipeSerializer 
        return serializers.RecipeDetailSerializer

    #  this is inbuilt method and way it seems , check resource url attached in video 87 or check DRF docs
    def perform_create(self, serializer):
        """ create a new recipe"""
        serializer.save(user=self.request.user)