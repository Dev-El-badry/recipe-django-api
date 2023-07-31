"""
Tests for the tags api
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def detial_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@example.com', password='simple123'):
    return get_user_model().objects.create_user(email, password)

class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for reteriving tags."""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_tags(self):
        """Test retrieving a list of tags"""
        Tag.objects.create(user=self.user, name='Tag1')
        Tag.objects.create(user=self.user, name='Tag2')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializers = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Tag1')
        tag = Tag.objects.create(user=self.user, name='Tag2')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After dinner')

        payload = {'name': 'Dessert'}
        url = detial_url(tag.id)
        res= self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detial_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_tags(self):
        """Test listing tags by those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Applies')
        tag2 = Tag.objects.create(user=self.user, name='Turkey')

        r1 = Recipe.objects.create(
            user=self.user,
            title='Recipe Test Name',
            time_minutes=5,
            price=Decimal('5.30')
        )
        r1.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag1 = Tag.objects.create(user=self.user, name='Eggs')
        Tag.objects.create(user=self.user, name='Lentils')

        r1 = Recipe.objects.create(
            user=self.user,
            title='Recipe Test Name',
            time_minutes=5,
            price=Decimal('5.30')
        )
        r2 = Recipe.objects.create(
            user=self.user,
            title='Recipe Test Name 2',
            time_minutes=5,
            price=Decimal('5.30')
        )
        r1.tags.add(tag1)
        r2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)