from django.test import TestCase
from django.urls import reverse, resolve
from dashboard_user_list.views import list_users


class TestUrls(TestCase):

    def test_list_url_resolves(self):
        url = reverse("userlist")
        print(resolve(url))
        self.assertEquals(resolve(url).func, list_users)
