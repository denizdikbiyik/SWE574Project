from django.test import TestCase
from django.urls import reverse
from social.models import Service, UserProfile, Event, ServiceApplication, UserRatings, NotifyUser, EventApplication, Tag, Log, Interest, Like, Featured, UserComplaints
from social.forms import ServiceForm, EventForm, ServiceApplicationForm, RatingForm, EventApplicationForm, ProfileForm, RequestForm
from social.views import ServiceCreateView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventCreateView, EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, ApplicationDeleteView, ApplicationEditView, FollowersListView, RemoveMyFollower, TimeLine, AllServicesView, AllEventsView, CreatedServicesView, CreatedEventsView, AppliedServicesView, ConfirmServiceTaken, ConfirmServiceGiven, RateUser, RateUserDelete, RateUserEdit, ServiceSearch, EventSearch, Notifications, EventApplicationDeleteView, AppliedEventsView, RequestCreateView, CreatedRequestsView, RequestsFromMeView, RequestDetailView, RequestDeleteView, ServiceFilter, AllUsersView, UsersServicesListView, UsersEventsListView, AddAdminView, RemoveAdminView, RecommendationsView
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from datetime import datetime

class AppliedEventsServicesViewTest(TestCase):
    def test_only_applied_events_in_list(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-11 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()

        test_event2 = Event.objects.create(
            eventcreater=test_user2, 
            eventname="ServiceTest2",
            eventdescription="ServiceTestDescription2", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-01 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event2.save()

        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')

        response = self.client.get(reverse('appliedevents'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # Check that initially we don't have any application in list
        self.assertTrue('eventapplied' in response.context)
        self.assertEqual(len(response.context['eventapplied']), 0)

        test_event_application = EventApplication.objects.create(
            date = '2022-01-02 10:00:00+03',
            applicant = test_user2,
            event = test_event,
            approved = True
        )
        test_event_application.save()

        response = self.client.get(reverse('appliedevents'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('eventapplied' in response.context)
        self.assertEqual(len(response.context['eventapplied']), 1)

    def test_only_applied_services_in_list(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-11 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        test_service2 = Service.objects.create(
            creater=test_user1, 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-10 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service2.save()

        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')

        response = self.client.get(reverse('appliedservices'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        # Check that initially we don't have any application in list
        self.assertTrue('serviceapplied' in response.context)
        self.assertEqual(len(response.context['serviceapplied']), 0)

        test_service_application = ServiceApplication.objects.create(
            applicant=test_user2,
            service=test_service
        )
        test_service_application.save()

        response = self.client.get(reverse('appliedservices'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('serviceapplied' in response.context)
        self.assertEqual(len(response.context['serviceapplied']), 1)

class AdminViewsTest(TestCase):
    def test_default_user_admin_false(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1_pk = str(test_user1.profile.pk)
        response = self.client.get(reverse('profile', kwargs={'pk':test_user1_pk}))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('profile' in response.context)
        self.assertEqual(response.context['profile'].isAdmin, False)

    def test_make_admin(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('add-admin', kwargs={'pk': test_user1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(username='testuser1').profile.isAdmin, True)

    def test_remove_admin(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.profile.isAdmin = True
        test_user2.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('remove-admin', kwargs={'pk': test_user1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.get(username='testuser1').profile.isAdmin, False)

class LoggingTest(TestCase):
    def test_addAdmin_log(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('add-admin', kwargs={'pk': test_user1.pk}))
        self.assertEqual(len(Log.objects.filter(operation="addadmin").filter(itemType="user").filter(itemId=test_user1.pk)), 1)

    def test_serviceApplication_log(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        test_service = Service.objects.create(
            creater=test_user1, 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-11 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()

        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')

        response = self.client.post(reverse('service-detail', kwargs={'pk': test_service.pk}))
        self.assertEqual(len(Log.objects.filter(operation="createserviceapplication").filter(itemType="service").filter(itemId=test_service.pk).filter(userId=test_user2.pk)), 1)

class DashboardViewTests(TestCase):
    def test_service_detail_shown_proper(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user3 = User.objects.create_user(username='testuser3', password='52J1vs0ZiDdRV')
        test_user1.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        test_user3.save()
        test_service = Service.objects.create(
            creater=test_user1,
            name="ServiceTest",
            description="ServiceTestDescription",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-11 10:00:00+03',
            capacity=5,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service.save()
        test_service_application = ServiceApplication.objects.create(
            applicant=test_user2,
            service=test_service
        )
        test_service_application2 = ServiceApplication.objects.create(
            applicant=test_user3,
            service=test_service
        )
        test_service_application.save()
        test_service_application2.save()

        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('dashboard-service-detail', kwargs={'pk':test_service.pk}))
        self.assertEqual(str(response.context['application_number']), '2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_active' in response.context)

    def test_event_detail_shown_proper(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user3 = User.objects.create_user(username='testuser3', password='52J1vs0ZiDdRV')
        test_user1.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        test_user3.save()
        test_event = Event.objects.create(
            eventcreater=test_user1,
            eventname="EventTest",
            eventdescription="EventTestDescription",
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-11 10:00:00+03',
            eventcapacity=5,
            eventduration=1
        )
        test_event.save()
        test_event_application = EventApplication.objects.create(
            applicant=test_user2,
            event=test_event
        )
        test_event_application2 = EventApplication.objects.create(
            applicant=test_user3,
            event=test_event
        )
        test_event_application.save()
        test_event_application2.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('dashboard-event-detail', kwargs={'pk': test_event.pk}))
        self.assertEqual(str(response.context['application_number']), '2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_active' in response.context)
        self.assertTrue('isDeleted' in response.context)

class RecommendationViewTests(TestCase):
    def user_with_recommendations_is_shown_recommendations(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.profile.isAdmin = True
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuL')
        test_user2.profile.isAdmin = True
        test_user2.save()

        test_interest = Interest.objects.create(user=test_user1, implicit=True, name="test",wiki_description="testing description")
        test_interest.save()

        test_recommendation1 = Service.objects.create(
            creater=test_user2,
            createddate=timezone.now,
            name="ServiceTest1",
            description="ServiceTestDescription",
            wiki_description="test as a(n) testing description",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate=timezone.now + timezone.timedelta(days=2),
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_recommendation1.save()

        test_recommendation2 = Service.objects.create(
            creater=test_user2,
            createddate=timezone.now,
            name="ServiceTest2",
            description="ServiceTestDescription",
            wiki_description="test as a(n) testing description",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate=timezone.now + timezone.timedelta(days=2),
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_recommendation2.save()

        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('recommendations'))
        self.assertEqual(response.context['recommendations_count'], 2)
        self.assertEqual(response.status_code, 200)


class ProfileViewTests(TestCase):
    def user_has_proper_number_of_interests(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.profile.isAdmin = True
        test_user1.save()

        test_interest = Interest.objects.create(user=test_user1, implicit=True, name="test", wiki_description="testing description")
        test_interest.save()

        test_interest2 = Interest.objects.create(user=test_user1, implicit=False, name="test2", wiki_description="testing2 description")
        test_interest2.save()

        test_interest3 = Interest.objects.create(user=test_user1, implicit=False, name="test3", wiki_description="testing2 description")
        test_interest3.save()

        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('profile'))
        self.assertEqual(len(response.context['interests']), 2)
        self.assertEqual(response.status_code, 200)

class FollowViewsTest(TestCase):
    def test_add_follower(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('add-follower', kwargs={'pk': test_user2.pk, 'followpk': test_user1.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(User.objects.get(username='testuser1').profile.followers.filter(username='testuser2')), 1)

    def test_remove_follower(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response1 = self.client.post(reverse('add-follower', kwargs={'pk': test_user2.pk, 'followpk': test_user1.pk}))
        response2 = self.client.post(reverse('remove-follower', kwargs={'pk': test_user2.pk, 'followpk': test_user1.pk}))
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(len(User.objects.get(username='testuser1').profile.followers.filter(username='testuser2')), 0)

class LikeViewsTest(TestCase):
    def test_like(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()
        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-11 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('event-like', kwargs={'pk': test_event.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Like.objects.filter(liked=test_user2.pk, itemType="event", itemId=test_event.pk)), 1)

    def test_unlike(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()
        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-11 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response1 = self.client.post(reverse('event-like', kwargs={'pk': test_event.pk}))
        response2 = self.client.post(reverse('event-unlike', kwargs={'pk': test_event.pk}))
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(len(Like.objects.filter(liked=test_user2.pk, itemType="event", itemId=test_event.pk)), 0)

class FeaturedViewsTest(TestCase):
    def test_featured(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-11 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('add-event-featured', kwargs={'pk': test_event.pk}))
        self.assertEqual(len(Featured.objects.filter(itemType="event", itemId=test_event.pk)), 1)

class ComplaintViewsTest(TestCase):
    def test_complaint(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user3 = User.objects.create_user(username='testuser3', password='8AB1vRV0G&3oM')
        test_user3.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        test_user3.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_complaint = UserComplaints.objects.create(
            complainted=test_user1, 
            complainter=test_user2,
            feedback="Fake user"
        )
        test_complaint.save()
        response = self.client.get(reverse('mycomplaints'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['complaints']), 1)

class DeactivateViewsTest(TestCase):
    def test_deactivated_event(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        test_event = Event.objects.create(
            eventcreater=test_user1, 
            eventname="ServiceTest",
            eventdescription="ServiceTestDescription", 
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate='2030-01-11 10:00:00+03',
            eventcapacity=1,
            eventduration=1
        )
        test_event.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('deactivate-event', kwargs={'pk': test_event.pk}))
        self.assertEqual(Event.objects.get(pk=test_event.pk).isActive, False)

    def test_deactivated(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('deactivate-user', kwargs={'pk': test_user1.pk}))
        self.assertEqual(User.objects.get(username='testuser1').profile.isActive, False)

    def test_activated(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user2.profile.isAdmin = True
        test_user1.save()
        test_user2.save()
        login = self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response1 = self.client.post(reverse('deactivate-user', kwargs={'pk': test_user1.pk}))
        response2 = self.client.post(reverse('activate-user', kwargs={'pk': test_user1.pk}))
        self.assertEqual(User.objects.get(username='testuser1').profile.isActive, True)
