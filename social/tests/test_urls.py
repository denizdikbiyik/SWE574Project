from django.test import TestCase
#from django.test import SimpleTestCase
from django.urls import reverse, resolve
from social.views import AllServicesView, ServiceDetailView, ServiceEditView, ServiceDeleteView

class URLTests(TestCase):
#class TestUrls(SimpleTestCase):

    def test_service_list_url_resolves(self):
        #assert 1 == 2
        url = reverse('allservices')
        #print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, AllServicesView)
    