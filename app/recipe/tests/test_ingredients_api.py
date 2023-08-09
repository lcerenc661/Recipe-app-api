"""Test for ingredients"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email='test@email.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


def create_ingredient(user, **params):
    default = {
        'name': 'Test Ingredient'
    }
    default.update(params)
    ingredient = Ingredient.objects.create(user=user, **default)
    return ingredient


def detail_view(ingredient_id):
    """Generates indredient detail URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsAPITest(TestCase):
    """Public Ingredients API test"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Auth requiered to request"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPI(TestCase):
    """Private Ingredients API tests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_list_ingredients(self):
        """Authenticated get request successful"""
        create_ingredient(user=self.user)
        create_ingredient(user=self.user)

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        user2 = create_user(email='user2@example.com')
        create_ingredient(user2)
        ingredient = create_ingredient(self.user)

        res = self.client.get(INGREDIENTS_URL)
        serializer = IngredientSerializer([ingredient], many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 1)

    def test_update_ingredients(self):
        """Test updating an ingredient."""
        ingredient = create_ingredient(user=self.user)
        payload = {'name': 'New name'}

        url = detail_view(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertTrue(Ingredient.objects.filter(
            name=payload['name']).exists())

    def test_deleting_ingredients(self):
        """Test deleting an ingredient"""
        ingredient = create_ingredient(user=self.user)

        url = detail_view(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())
