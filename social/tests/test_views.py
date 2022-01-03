from django.test import TestCase
from django.urls import reverse
from social.models import Service, UserProfile, Event, ServiceApplication, UserRatings, NotifyUser, EventApplication, Tag
from social.forms import ServiceForm, EventForm, ServiceApplicationForm, RatingForm, EventApplicationForm, ProfileForm, RequestForm
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
