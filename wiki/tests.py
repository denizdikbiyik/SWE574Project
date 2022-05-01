from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('wiki'))
        self.assertEqual(response.status_code, 200)
