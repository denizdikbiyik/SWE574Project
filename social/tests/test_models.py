from datetime import datetime
from django.test import TestCase

from django.contrib.auth.models import User
from social.models import Service, Feedback, UserProfile, Event, ServiceApplication

class ServiceModelTest(TestCase):              
    @classmethod

    def setUp(self):
        self.u1 = User.objects.create(username='usertest1')

    def testService(self):
        service = Service(
            creater=self.u1, 
            createddate=datetime.now, 
            name="ServiceTest",
            picture='uploads/service_pictures/default.png',
            description="ServiceTestDescription",   
            servicedate=datetime.now,
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
            )
        self.assertEqual(service.creater, self.u1)
        self.assertEqual(service.createddate, datetime.now)
        self.assertEqual(service.name, "ServiceTest")

    def tearDown(self):
        self.u1.delete()

    # def setUpTestData(self):                                     
    #     self.service = Service.objects.create(
    #         creater=self.u1,
    #         createddate=datetime.now,
    #         name="ServiceTest",
    #         picture='uploads/service_pictures/default.png',
    #         description="ServiceTestDescription",   
    #         servicedate=datetime.now,
    #         capacity=1,
    #         duration=1,
    #         is_given=False,
    #         is_taken=False
    #     ) 

    # def test_it_has_information_fields(self):                   
    #     self.assertIsInstance(self.service.description, str)

    # def test_it_has_timestamps(self):                           
    #     self.assertIsInstance(self.service.servicedate, datetime)