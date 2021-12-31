from django.test import TestCase
from django.urls import reverse, resolve
from social.views import ServiceCreateView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventCreateView, EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, ApplicationDeleteView, ApplicationEditView, FollowersListView, RemoveMyFollower, TimeLine, AllServicesView, AllEventsView, CreatedServicesView, CreatedEventsView, AppliedServicesView, ConfirmServiceTaken, ConfirmServiceGiven, RateUser, RateUserDelete, RateUserEdit, ServiceSearch, EventSearch, Notifications, EventApplicationDeleteView, AppliedEventsView, RequestCreateView, CreatedRequestsView, RequestsFromMeView, RequestDetailView, RequestDeleteView, ServiceFilter

class URLTests(TestCase):

    def test_service_create_url_resolves(self):
        url = reverse('service-create')
        self.assertEquals(resolve(url).func.view_class, ServiceCreateView)

    def test_service_list_url_resolves(self):
        url = reverse('allservices')
        self.assertEquals(resolve(url).func.view_class, AllServicesView)

    def test_service_list_url_resolves(self):
        url = reverse('createdservices')
        self.assertEquals(resolve(url).func.view_class, CreatedServicesView)

    def test_service_list_url_resolves(self):
        url = reverse('appliedservices')
        self.assertEquals(resolve(url).func.view_class, AppliedServicesView)

    def test_service_list_url_resolves(self):
        url = reverse('service-detail')
        self.assertEquals(resolve(url).func.view_class, ServiceDetailView)

    def test_service_list_url_resolves(self):
        url = reverse('service-edit')
        self.assertEquals(resolve(url).func.view_class, ServiceEditView)

    def test_service_list_url_resolves(self):
        url = reverse('service-delete')
        self.assertEquals(resolve(url).func.view_class, ServiceDeleteView)
    
    def test_service_list_url_resolves(self):
        url = reverse('profile')
        self.assertEquals(resolve(url).func.view_class, ProfileView)

    def test_service_list_url_resolves(self):
        url = reverse('profile-edit')
        self.assertEquals(resolve(url).func.view_class, ProfileEditView)
    
    def test_service_list_url_resolves(self):
        url = reverse('event-create')
        self.assertEquals(resolve(url).func.view_class, EventCreateView)

    def test_service_list_url_resolves(self):
        url = reverse('allevents')
        self.assertEquals(resolve(url).func.view_class, AllEventsView)

    def test_service_list_url_resolves(self):
        url = reverse('createdevents')
        self.assertEquals(resolve(url).func.view_class, CreatedEventsView)

    def test_service_list_url_resolves(self):
        url = reverse('event-detail')
        self.assertEquals(resolve(url).func.view_class, EventDetailView)

    def test_service_list_url_resolves(self):
        url = reverse('event-edit')
        self.assertEquals(resolve(url).func.view_class, EventEditView)

    def test_service_list_url_resolves(self):
        url = reverse('event-delete')
        self.assertEquals(resolve(url).func.view_class, EventDeleteView)

    def test_service_list_url_resolves(self):
        url = reverse('add-follower')
        self.assertEquals(resolve(url).func.view_class, AddFollower)

    def test_service_list_url_resolves(self):
        url = reverse('remove-follower')
        self.assertEquals(resolve(url).func.view_class, RemoveFollower)

    def test_service_list_url_resolves(self):
        url = reverse('remove-my-follower')
        self.assertEquals(resolve(url).func.view_class, RemoveMyFollower)

    def test_service_list_url_resolves(self):
        url = reverse('application-delete')
        self.assertEquals(resolve(url).func.view_class, ApplicationDeleteView)

    def test_service_list_url_resolves(self):
        url = reverse('application-edit')
        self.assertEquals(resolve(url).func.view_class, ApplicationEditView)

    def test_service_list_url_resolves(self):
        url = reverse('confirm-service-taken')
        self.assertEquals(resolve(url).func.view_class, ConfirmServiceTaken)

    def test_service_list_url_resolves(self):
        url = reverse('confirm-service-given')
        self.assertEquals(resolve(url).func.view_class, ConfirmServiceGiven)

    def test_service_list_url_resolves(self):
        url = reverse('followers')
        self.assertEquals(resolve(url).func.view_class, FollowersListView)

    def test_service_list_url_resolves(self):
        url = reverse('rateuser')
        self.assertEquals(resolve(url).func.view_class, RateUser)

    def test_service_list_url_resolves(self):
        url = reverse('rating-edit')
        self.assertEquals(resolve(url).func.view_class, RateUserEdit)

    def test_service_list_url_resolves(self):
        url = reverse('rating-delete')
        self.assertEquals(resolve(url).func.view_class, RateUserDelete)

    def test_service_list_url_resolves(self):
        url = reverse('timeline')
        self.assertEquals(resolve(url).func.view_class, TimeLine)

    def test_service_list_url_resolves(self):
        url = reverse('service-search')
        self.assertEquals(resolve(url).func.view_class, ServiceSearch)

    def test_service_list_url_resolves(self):
        url = reverse('event-search')
        self.assertEquals(resolve(url).func.view_class, EventSearch)

    def test_service_list_url_resolves(self):
        url = reverse('notifications')
        self.assertEquals(resolve(url).func.view_class, Notifications)

    def test_service_list_url_resolves(self):
        url = reverse('event-application-delete')
        self.assertEquals(resolve(url).func.view_class, EventApplicationDeleteView)

    def test_service_list_url_resolves(self):
        url = reverse('appliedevents')
        self.assertEquals(resolve(url).func.view_class, AppliedEventsView)

    def test_service_list_url_resolves(self):
        url = reverse('request-create')
        self.assertEquals(resolve(url).func.view_class, RequestCreateView)

    def test_service_list_url_resolves(self):
        url = reverse('createdrequests')
        self.assertEquals(resolve(url).func.view_class, CreatedRequestsView)

    def test_service_list_url_resolves(self):
        url = reverse('requestsfromme')
        self.assertEquals(resolve(url).func.view_class, RequestsFromMeView)

    def test_service_list_url_resolves(self):
        url = reverse('request-detail')
        self.assertEquals(resolve(url).func.view_class, RequestDetailView)

    def test_service_list_url_resolves(self):
        url = reverse('request-delete')
        self.assertEquals(resolve(url).func.view_class, RequestDeleteView)

    def test_service_list_url_resolves(self):
        url = reverse('service-filter')
        self.assertEquals(resolve(url).func.view_class, ServiceFilter)
