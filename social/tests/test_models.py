from datetime import datetime
from django.test import TestCase

from django.contrib.auth.models import User
from social.models import Service, UserProfile, Event, ServiceApplication, UserRatings, NotifyUser, EventApplication, Tag

class ServiceModelTest(TestCase):              
    @classmethod

    def setUp(self):
        self.u1 = User.objects.create(username='usertest1')

    def testService(self):
        service = Service(
            creater=self.u1, 
            createddate=datetime.now, 
            name="ServiceTest",
            description="ServiceTestDescription", 
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate=datetime.now,
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
            )
        self.assertEqual(service.creater, self.u1)
        self.assertEqual(service.createddate, datetime.now)
        self.assertEqual(service.name, "ServiceTest")

    def testEvent(self):
        event = Event(
            eventcreater=self.u1, 
            eventcreateddate=datetime.now, 
            eventname="EventTest",
            eventdescription="EventTestDescription", 
            eventpicture='uploads/event_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate=datetime.now,
            eventcapacity=1,
            eventduration=1
            )
        self.assertEqual(event.eventcreater, self.u1)
        self.assertEqual(event.eventcreateddate, datetime.now)
        self.assertEqual(event.eventname, "EventTest")

    def tearDown(self):
        self.u1.delete()

