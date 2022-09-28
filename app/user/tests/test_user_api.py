from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
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



