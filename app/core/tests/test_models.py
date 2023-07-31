"""
    Tests for models
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

from unittest.mock import patch

def create_user(email='test@example.com', password='simple123'):
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """Test mdoel."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "computer@null.com"
        password = "password"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_email_normalized(self):
        """Tests email is normalized for new users"""
        smaple_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@EXAMPLE.COM', 'test4@example.com'],
        ]

        for email, expected in smaple_emails:
            user = get_user_model().objects.create_user(email, 'simple123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            user = get_user_model().objects.create_user('', 'simple123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_crate_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """test creating a ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name="Test Name")

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')