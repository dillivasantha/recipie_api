"""Tests for Django admin modifications"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTests(TestCase):
    """Tests for Django Admin"""

    def setUp(self):
        """ Create user and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email = 'admin@example.com',
            password= 'testpass123'
        )
        # forces to login with super user details
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email = 'testuser@example.com',
            password = 'test123'
        )

    def test_users_list(self):
        """Test the users are listed on page """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res,self.user.email)
        self.assertContains(res,self.user.name)

    def test_edit_user_page(self):
        """Test by change user details"""
        url = reverse('admin:core_user_change',args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_add_user_page(self):
        """ Test to create user page """
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code,200)