"""Test for the tags API"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email="userr@example.com", password='testpassword123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_requiered(self):
        """Test auth is required for retrieving tags"""

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrive_tags_successful(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(name='tag1', user=self.user)
        Tag.objects.create(name='tag2', user=self.user)

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test tag list is limited to authenticated user."""
        user2 = create_user(email='thisneweamil@gmail.com')
        Tag.objects.create(name='tag1', user=user2)
        Tag.objects.create(name='tag1', user=user2)

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_update_tag(self):
        """Test update a tag successful"""
        tag = Tag.objects.create(
            name='Vegans',
            user=self.user
        )

        payload = {'name': 'VEGAN'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(
            user=self.user,
            name='Dessert'
        )

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags by those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Vegetarian')
        tag2 = Tag.objects.create(user=self.user, name='Mexican')
        recipe = Recipe.objects.create(
            title='Tacos',
            time_minutes=25,
            price=Decimal('5.00'),
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_tags_list_unique(self):
        """Test filtered tags by assigned returns a unique list."""
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Thai')
        recipe1 = Recipe.objects.create(
            title='Vegan Hamburger',
            time_minutes=20,
            price=Decimal('7.25'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title="Vegan Crepe",
            time_minutes=30,
            price=Decimal('10.45'),
            user=self.user
        )
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
