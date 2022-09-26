"""
Test for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    """Test Models."""
    def test_create_user_with_email_successfull(self):
        """Test creating a user with email is succesfull or not"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password= password,
            )
        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_normalise_email(self):
        """ normalising email """
        sample_emails = [['test1@EXAMPLE.com','test1@example.com'],
                        ['Test2@Example.com','Test2@example.com'],
                        ['TEST3@EXAMPLe.COM ', 'TEST3@example.com']]
        for email,expected in sample_emails:
            user = get_user_model().objects.create_user(email,'samplepass123')
            self.assertEqual(user.email,expected)

    def test_new_user_without_email_raises_error(self):
        """test to raise value error when empty email is passed"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('','samplepass123')

    def test_super_user_creation(self):
        """test to creation of super user and its flags"""
        user = get_user_model().objects.create_superuser('testsuper@example.com','superpass123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)