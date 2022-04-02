from django.test import TestCase
from django.urls import reverse, resolve
from dashboard_event_list.views import list_events


class TestUrls(TestCase):

    def test_list_url_resolves(self):
        url = reverse("eventlist")
        print(resolve(url))
        self.assertEquals(resolve(url).func, list_events)
