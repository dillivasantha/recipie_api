from decimal import Decimal
from recipe.serializers import TagSerialzer
from core.models  import Tag
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model


from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list') #app_name:model_name-action

def detail_url(tag_id):
    """ create and return a tag detail url """
    return reverse('recipe:tag-detail',args=[tag_id]) #app_name:model_name-action

def create_user(**params):
    """ create a user for testing """
    return get_user_model().objects.create_user(**params)
def create_tag(**params):
    """ creating tag which can be used in testing purposes"""
    return Tag.objects.create(**params)
class PublicTagApiTests(TestCase):
    """Test an un authenticated API Tests"""
    def setUp(self) -> None:
        self.client = APIClient()
    def test_unauthorized_tag_access(self):
        """ test for an unauthorixzed access api"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagApiTests(TestCase):
    """ Test an authenticated API Tests"""
    def setUp(self) -> None:
        self.user = create_user(email='user@example.com',password = 'testpass123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test retrieving a list of tags """
        tag1 = create_tag(user=self.user,name ='Vegan')
        tag2 = create_tag(user=self.user, name="Dessert")

        #hit api amd retieve 
        res = self.client.get(TAGS_URL)

        # get from db 
        tags = Tag.objects.all().order_by('-name') # ordering by name 
        # pass this to serialzer and make it serialzed 
        serializer=TagSerialzer(tags,many=True)
        #now compare this serialzed data and res data 
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)
    
    def test_tags_limited_to_user(self):
        """ test list of tags is limited to authenticated user """
        user2 = create_user(email='user2@example.com',password='test123')
        tag_1 = create_tag(user = user2,name ='Fruity')
        tag_2 = create_tag(user = self.user,name = 'Comfort Food')

        res = self.client.get(TAGS_URL) # by default gives the tags linked to user asigned in setUP 
        # which is only 1 tag that is Comfort Food
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        # no need to get data from and serialze it and compare that data with res data , 
        # because we are just calculating counts and verifying names 
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],tag_2.name)

    def test_update_tag(self):
        """ Test updating a tag"""
        tag = Tag.objects.create(user=self.user,name = 'After Dinner')
        payload={'name':'Dessert_ICE'}
        url = detail_url(tag.id)
        res = self.client.patch(url,payload)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name,payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag assigned to user"""
        tag = Tag.objects.create(user=self.user,name='Breakfast')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        tags_now = Tag.objects.filter(id=tag.id)
        self.assertFalse(tags_now.exists())

   
