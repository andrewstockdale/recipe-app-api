from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
  return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
  def setUp(self):
    self.client = APIClient()
  
  def test_create_valid_user_success(self):
      payload = {
        'email': 'test@gmail.com',
        'password': 'password',
        'name': 'Name'
      }
      res = self.client.post(CREATE_USER_URL, payload)
      self.assertEqual(res.status_code, status.HTTP_201_CREATED)
      user = get_user_model().objects.get(**res.data)
      self.assertTrue(user.check_password(payload['password']))
      self.assertNotIn('password', res.data)

  def test_user_exists(self):
    payload = {'email': 'test@gmail.com', 'password': 'testpass', 'name':'Name'}
    create_user(**payload)

    res = self.client.post(CREATE_USER_URL, payload)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_password_too_short(self):
    payload = {'email': 'test@gmail.com', 'password': 'oop', 'name':'Test'}
    res = self.client.post(CREATE_USER_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    userExists = get_user_model().objects.filter(
      email=payload["email"]
    ).exists()
    self.assertFalse(userExists)
  
  def test_create_token_for_user(self):
    """Test that a token is created"""
    payload = {
      'email': 'test@gmail.com',
      'password': 'password'
    }
    create_user(**payload)
    res = self.client.post(TOKEN_URL, payload)
  
    self.assertIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_200_OK)

  
  def test_create_token_invalid_credentials(self):
    user = create_user(email='test@gmail.com', password='testpass')
    payload = {'email': user.email, 'password':' wrong'}
    res = self.client.post(TOKEN_URL, payload)

    self.assertNotIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_create_token_no_user(self):
    payload = {'email': 'test@gmail.com', 'password': 'password'}
    res = self.client.post(TOKEN_URL, payload)

    self.assertNotIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  def test_create_token_missing_field(self):
    res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
  
    self.assertNotIn('token', res.data)
    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)