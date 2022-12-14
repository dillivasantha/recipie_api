"""
Tests for recipe APIs
"""
from decimal import Decimal
import email

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Recipe,Tag)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list') #app_name:model_name-action

def detail_url(recipe_id):
    """create and return a recipe details URL."""
    return reverse('recipe:recipe-detail',args=[recipe_id]) 

# helper class which will be helpful below in testing , this is not original create recipe(will be seperate test)  
def create_recipe(user,**params):
    """create and returns a sample recipe"""
    defaults={
        'title':'sample recipe api',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description':'Sample description',
        'link':'http://example.com/recipe.pdf'
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user,**defaults)
    return recipe

def create_user(**params):
        """creating user for email and password passed"""
        return get_user_model().objects.create_user(**params)

class PublicRecipeAPITests(TestCase):
    """ Test un authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """test authenticateion is required , and through error"""
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)
        

class PrivateReccipeAPITests(TestCase):
    """ Test with authentication provided"""

    
    def setUp(self) -> None:
        self.user = create_user(email='user@example.com',password='user123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test recieving a list of recipes """
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user """
        other_user = create_user(email='other@example.com',password='password123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        # data while hitting url 
        res = self.client.get(RECIPES_URL)
        # data from data base 
        recipes=Recipe.objects.filter(user=self.user)
        serializer= RecipeSerializer(recipes,many=True)
        # now comparing 
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)


    def test_get_recipe_detail(self):
        """Test to get recipe details"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id) # as url cannot be same for every recipe , we need to append id to url so using functions
        res=self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)# as its sa single record we are not passing many -= true
        self.assertEqual(res.data,serializer.data)

    def test_create_recipe(self):# we are not using above helper class , we are actually creatingby sending payload and post call
        """Test creating a recipe"""
        payload={
            'title':'sample new recipe',
            'time_minutes':30,
            'price':Decimal('5.99')

        }
        res= self.client.post(RECIPES_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipe_created = Recipe.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(recipe_created,k),v) # to compare values of create recipe and sent payload equal or not
        self.assertEqual(recipe_created.user,self.user)

    def test_partial_update(self):
        """ Test partial update of a recipe"""
        original_link="https://example.com//recipe.pdf"
        recipe= create_recipe(
            user=self.user,
            title = 'sample recipe title',
            link=original_link,
             )
        payload={'title':'updated title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url,payload)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.user,self.user)
        self.assertEqual(recipe.link,original_link)
    
    def test_full_Update(self):
        """Test full update of a recipe"""
        recipe = create_recipe(
            user = self.user,
            title='sample recipe title',
            price = Decimal('9.99'),
            link='https://example.com//recipe.pdf',
            description='sample description',
        )
        payload = {
            "title":'sample new recipe title',
            "price" : Decimal('7.99'),
            "link":'https://example.com//new-recipe.pdf',
            'description':'new description',
            'time_minutes':10
        }
        url = detail_url(recipe.id)
        res= self.client.put(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(recipe.user,self.user)
        for k,v in payload.items():
            self.assertEqual(getattr(recipe,k),v)


    def test_update_user_returns_error(self):
        """ Test changing the user results in an error."""
        new_user = create_user(email='user2@example.com',password='test123')
        recipe = create_recipe(user=self.user)
        payload = {'user':new_user.id}
        url = detail_url(recipe.id)
        res = self.client.patch(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user,self.user) # need to check 

    def test_delete_recipe(self):
        """Test deleting a recipe Succesfull """
        recipe= create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists()) # which means above created recipe is deleted and no other recipe exists now 

    def test_delete_other_user_recipe(self):
        """Test trying to delete other user recipe gives errror"""
        new_user = create_user(email='user2@example.com',password='pass123')
        recipe= create_recipe(user=new_user)
        url = detail_url(recipe.id)
        res=self.client.delete(url)

        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

     #introducing nested serializer concept as the tags json objects present inside recipe payload
    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Thai prawn curry',
            'time_minutes': 30,
            'price':Decimal('2.50'),
            'tags':[{'name':'Thai'},{'name':'Dinner'}]

        }
        res = self.client.post(RECIPES_URL,payload,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe=recipes[0]
        self.assertEqual(recipe.tags.count(),2)
        for tag in payload['tags']:
            exists=recipe.tags.filter(name =tag['name'],user=self.user).exists()
            self.assertTrue(exists)
    
    # tags not to duplicate , so we dont create a new tag if it exists already 
    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name ='Indian')
        paylod={
            'title': 'Pongal',
            'time_minutes': 20,
            'price':Decimal('4.50'),
            'tags':[{'name':'Indian'},{'name':'Breakfast'}]


        }
        res = self.client.post(RECIPES_URL,paylod,format='json')
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe= recipes[0]
        self.assertEqual(recipe.tags.count(),2)
        self.assertIn(tag_indian,recipe.tags.all())
        for tag in paylod['tags']:
            exists = recipe.tags.filter(name=tag['name'],user = self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe"""
        recipe = create_recipe(user=self.user)
        payload = {'tags':[{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url,payload,format='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user,name = 'Lunch')
        self.assertIn(new_tag,recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""
        tag_breakfast = Tag.objects.create(user = self.user,name ='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name = 'Lunch')
        payload = {'tags':[{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url,payload, format ='json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(tag_lunch,recipe.tags.all())
        self.assertNotIn(tag_breakfast,recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tag."""
        tag = Tag.objects.create(user = self.user,name='Dessert')
        recipe = create_recipe(user = self.user)
        recipe.tags.add(tag)

        payload = {'tags':[]}
        url = detail_url(recipe.id)
        res = self.client.patch(url,payload,format = 'json')
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(recipe.tags.all()),0)
        # self.assertEqual(recipe.tags.count(),0)