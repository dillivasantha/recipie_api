from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the public features of the user"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successfull."""
        payload={
            'email':'test1@example.com',
            'password':'testpass123',
            'name':'test1'
        }
        res=self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        # validate the password is not returned
        self.assertNotIn('password',res.data)
        # retrieve the user which created above and check if its really created
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

    def test_email_user_exists_error(self):
        """Test to check if email already exists"""
        payload={
            'email':'test1@example.com',
            'password':'testpass123',
            'name':'test name'
        }
        create_user(**payload)
        res=self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test to check password length """
        payload={
            'email':'test1@example.com',
            'password':'123',
            'name':'test name'
        }
        res = self.client.post(CREATE_USER_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        user_details = {
            'name':'test1',
            'email': 'test1@example.com',
            'password':'testpass123'
        }
        create_user(**user_details)

        payload = {
            'email':user_details['email'],
            'password':user_details['password']
        }

        res = self.client.post(TOKEN_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('token',res.data)

    def test_create_token_bad_credentials(self):
        """ test if we pass bad credentials to generate token"""
        user_details = {
            'name':'test1',
            'email': 'test1@example.com',
            'password':'testpass123'
        }
        create_user(**user_details)

        payload = {
            'email':user_details['email'],
            'password':'wrongpassword'
        }
        res = self.client.post(TOKEN_URL,payload)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token',res.data)

    def test_create_token_blank_password(self):
        """test to return error if blank password is sent"""
        create_user(email='test1@example.com',password='goodpassw') # creating a user
        payload= {'email':'test1@example.com','password':''} # pasing blank password intentionally
        res=self.client.post(TOKEN_URL,payload) # post call with above payload so that it fails
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token',res.data)

    def test_retrieve_user_unauthorized(self):
        """test authentication is required for users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """ Test api that requires authentication """
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password= 'testpasss123',
            name = 'Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name':self.user.name,
            'email':self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test post is not allowed for me endpoint"""
        res = self.client.post(ME_URL,{'test':'anyjson'})
        self.assertEqual(res.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'name':'updatedname','password':'newpassword'}
        res = self.client.patch(ME_URL,payload)
        self.user.refresh_from_db()
        self.assertTrue(res.status_code,status.HTTP_200_OK)
        self.assertEqual(self.user.name,payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))