from django.test import TestCase
from django.urls import reverse, resolve
from social.views import ServiceCreateView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventCreateView, EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, ApplicationDeleteView, ApplicationEditView, FollowersListView, RemoveMyFollower, TimeLine, AllServicesView, AllEventsView, CreatedServicesView, CreatedEventsView, AppliedServicesView, ConfirmServiceTaken, ConfirmServiceGiven, RateUser, RateUserDelete, RateUserEdit, ServiceSearch, EventSearch, Notifications, EventApplicationDeleteView, AppliedEventsView, RequestCreateView, CreatedRequestsView, RequestsFromMeView, RequestDetailView, RequestDeleteView, ServiceFilter

from django.contrib.auth.models import User
from social.models import Service, UserProfile, Event, ServiceApplication, UserRatings, NotifyUser, EventApplication, Tag

class URLTests(TestCase):

    def test_service_create_url_resolves(self):
        url = reverse('service-create')
        self.assertEquals(resolve(url).func.view_class, ServiceCreateView)

    def test_all_services_url_resolves(self):
        url = reverse('allservices')
        self.assertEquals(resolve(url).func.view_class, AllServicesView)

    def test_created_services_url_resolves(self):
        url = reverse('createdservices')
        self.assertEquals(resolve(url).func.view_class, CreatedServicesView)

    def test_applied_services_url_resolves(self):
        url = reverse('appliedservices')
        self.assertEquals(resolve(url).func.view_class, AppliedServicesView)

    def test_service_detail_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            createddate='2022-01-01 10:00:00+03', 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-01 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        url = reverse('service-detail', args=[str(test_service.pk)])
        self.assertEquals(resolve(url).func.view_class, ServiceDetailView)

    def test_service_edit_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            createddate='2022-01-01 10:00:00+03', 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-01 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        url = reverse('service-edit', args=[str(test_service.pk)])
        self.assertEquals(resolve(url).func.view_class, ServiceEditView)

    def test_service_delete_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            createddate='2022-01-01 10:00:00+03', 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-01 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        url = reverse('service-delete', args=[str(test_service.pk)])
        self.assertEquals(resolve(url).func.view_class, ServiceDeleteView)
    
    def test_profile_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        url = reverse('profile', args=[str(test_user1.pk)])
        self.assertEquals(resolve(url).func.view_class, ProfileView)

    def test_profile_edit_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()
        url = reverse('profile-edit', args=[str(test_user1.pk)])
        self.assertEquals(resolve(url).func.view_class, ProfileEditView)
    
    def test_event_create_url_resolves(self):
        url = reverse('event-create')
        self.assertEquals(resolve(url).func.view_class, EventCreateView)

    def test_all_events_url_resolves(self):
        url = reverse('allevents')
        self.assertEquals(resolve(url).func.view_class, AllEventsView)

    def test_created_events_url_resolves(self):
        url = reverse('createdevents')
        self.assertEquals(resolve(url).func.view_class, CreatedEventsView)

    def test_event_detail_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventcreateddate='2022-01-01 10:00:00+03', 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-01 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()

        url = reverse('event-detail', args=[str(test_event.pk)])
        self.assertEquals(resolve(url).func.view_class, EventDetailView)

    def test_event_edit_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventcreateddate='2022-01-01 10:00:00+03', 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-01 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()

        url = reverse('event-edit', args=[str(test_event.pk)])
        self.assertEquals(resolve(url).func.view_class, EventEditView)

    def test_event_delete_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventcreateddate='2022-01-01 10:00:00+03', 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-01 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()
        
        url = reverse('event-delete', args=[str(test_event.pk)])
        self.assertEquals(resolve(url).func.view_class, EventDeleteView)

    def test_add_follower_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        url = reverse('add-follower', args=[str(test_user1.pk),str(test_user2.pk)])
        self.assertEquals(resolve(url).func.view_class, AddFollower)

    def test_remove_follower_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        url = reverse('remove-follower', args=[str(test_user1.pk),str(test_user2.pk)])
        self.assertEquals(resolve(url).func.view_class, RemoveFollower)

    def test_application_delete_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            createddate='2022-01-01 10:00:00+03', 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-01 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        test_service_application = ServiceApplication.objects.create(
            applicant=test_user2,
            service=test_service
        )
        test_service_application.save()

        url = reverse('application-delete', args=[str(test_service.pk),str(test_service_application.pk)])
        self.assertEquals(resolve(url).func.view_class, ApplicationDeleteView)

    def test_application_edit_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            createddate='2022-01-01 10:00:00+03', 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-01 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        test_service_application = ServiceApplication.objects.create(
            applicant=test_user2,
            service=test_service
        )
        test_service_application.save()

        url = reverse('application-edit', args=[str(test_service.pk),str(test_service_application.pk)])
        self.assertEquals(resolve(url).func.view_class, ApplicationEditView)

    def test_confirm_service_taken_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            createddate='2022-01-01 10:00:00+03', 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-01 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        url = reverse('confirm-service-taken', args=[str(test_service.pk)])
        self.assertEquals(resolve(url).func.view_class, ConfirmServiceTaken)

    def test_confirm_service_given_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            createddate='2022-01-01 10:00:00+03', 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-01 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        url = reverse('confirm-service-given', args=[str(test_service.pk)])
        self.assertEquals(resolve(url).func.view_class, ConfirmServiceGiven)

    def test_followers_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        url = reverse('followers', args=[str(test_user1.pk)])
        self.assertEquals(resolve(url).func.view_class, FollowersListView)

    def test_timeline_url_resolves(self):
        url = reverse('timeline')
        self.assertEquals(resolve(url).func.view_class, TimeLine)

    def test_service_search_url_resolves(self):
        url = reverse('service-search')
        self.assertEquals(resolve(url).func.view_class, ServiceSearch)

    def test_event_search_url_resolves(self):
        url = reverse('event-search')
        self.assertEquals(resolve(url).func.view_class, EventSearch)

    def test_notifications_url_resolves(self):
        url = reverse('notifications')
        self.assertEquals(resolve(url).func.view_class, Notifications)

    def test_event_application_delete_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventcreateddate='2022-01-01 10:00:00+03', 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-01 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()

        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.save()

        test_event_application = EventApplication.objects.create(
            applicant=test_user2,
            event=test_event
        )
        test_event_application.save()

        url = reverse('event-application-delete', args=[str(test_event.pk),str(test_event_application.pk)])
        self.assertEquals(resolve(url).func.view_class, EventApplicationDeleteView)

    def test_appliedevents_url_resolves(self):
        url = reverse('appliedevents')
        self.assertEquals(resolve(url).func.view_class, AppliedEventsView)

    def test_request_create_url_resolves(self):
        url = reverse('request-create')
        self.assertEquals(resolve(url).func.view_class, RequestCreateView)

    def test_created_requests_url_resolves(self):
        url = reverse('createdrequests')
        self.assertEquals(resolve(url).func.view_class, CreatedRequestsView)

    def test_requests_from_me_url_resolves(self):
        url = reverse('requestsfromme')
        self.assertEquals(resolve(url).func.view_class, RequestsFromMeView)

    def test_request_detail_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        test_request = Tag.objects.create(
            tag='testTag',
            requester=test_user1,
            toPerson=test_user2
        )
        test_request.save()

        url = reverse('request-detail', args=[str(test_request.pk)])
        self.assertEquals(resolve(url).func.view_class, RequestDetailView)

    def test_request_delete_url_resolves(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        test_request = Tag.objects.create(
            tag='testTag',
            requester=test_user1,
            toPerson=test_user2
        )
        test_request.save()

        url = reverse('request-delete', args=[str(test_request.pk)])
        self.assertEquals(resolve(url).func.view_class, RequestDeleteView)

    def test_service_filter_url_resolves(self):
        url = reverse('service-filter')
        self.assertEquals(resolve(url).func.view_class, ServiceFilter)
