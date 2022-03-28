from django.test import TestCase
from django.urls import reverse, resolve
from dashboard_service_list.views import list_services


class TestUrls(TestCase):

    def test_list_url_resolves(self):
        url = reverse("servicelist")
        print(resolve(url))
        self.assertEquals(resolve(url).func, list_services)
