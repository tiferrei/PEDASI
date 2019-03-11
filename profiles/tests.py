from django.test import Client, TestCase
from django.urls import reverse

from rest_framework.authtoken.models import Token

from . import models


class UserTest(TestCase):
    def test_user_uri(self):
        """
        Test that we can get a URI for a user.
        """
        user = models.User.objects.create_user('Test User')
        uri = user.get_uri()

        self.assertEqual(str, type(uri))
        self.assertLessEqual(1, len(uri))

        client = Client()
        response = client.get(uri)

        self.assertEqual(200, response.status_code)

        content = response.json()
        self.assertIn('status', content)
        self.assertIn('data', content)

        data = content['data']
        self.assertIn('user', data)
        self.assertIn('pk', data['user'])
        self.assertEqual(user.pk, data['user']['pk'])

    def test_user_get_token(self):
        """
        Check that we can get an API Token for a given user.
        """
        user = models.User.objects.create_user('Test User')

        client = Client()
        client.force_login(user)

        with self.assertRaises(Token.DoesNotExist):
            # User should not already have token
            token = Token.objects.get(user=user)

        response = client.get(reverse('profiles:token', kwargs={'pk': user.pk}))

        self.assertEqual(200, response.status_code)

        content = response.json()
        self.assertIn('status', content)
        self.assertIn('data', content)
        self.assertEqual('success', content['status'])

        data = content['data']
        self.assertIn('token', data)
        self.assertIn('key', data['token'])

        key = data['token']['key']

        token = Token.objects.get(user=user)

        self.assertEqual(key, token.key)
