from django.test import Client, TestCase

from .models import User


class UserTest(TestCase):
    def test_user_uri(self):
        """
        Test that we can get a URI for a user.
        """
        user = User.objects.create_user('Test User')
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
