from django.http import HttpRequest
from django.test import TestCase, Client
from django.urls import reverse
import datetime
from dashboard_service_list.views import make_context_for_service_list, make_query_for_service_list
from social.models import Service
from django.contrib.auth.models import User

from django.utils import timezone


class TestViews(TestCase):

    # P
    def test_url_exists(self):
        client = Client()
        response = client.get("/dashboard/servicelist/")
        self.assertEqual(response.status_code, 404)

    def test_make_context_for_service_list(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.profile.isAdmin = True
        test_user1.save()
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        date_today = datetime.datetime.now()

        def create_date_before_given_date(days, date):
            date_before = (date - datetime.timedelta(days=days))
            return date_before

        def create_date_after_given_date(days, date):
            date_after = (date + datetime.timedelta(days=days))
            return date_after

        # 1. included only in all
        test_service1 = Service.objects.create(
            creater=test_user1,
            createddate=create_date_before_given_date(500, date_today),
            name="ServiceTest1",
            description="ServiceTestDescription",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate=create_date_after_given_date(7, create_date_before_given_date(500, date_today)),
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service1.save()

        # 2. included only in all & month & week
        test_service2 = Service.objects.create(
            creater=test_user1,
            createddate=create_date_before_given_date(2, date_today),
            name="ServiceTest2",
            description="ServiceTestDescription",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate=create_date_after_given_date(7, create_date_before_given_date(2, date_today)),
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service2.save()

        # 3. included only in all & month
        test_service3 = Service.objects.create(
            creater=test_user1,
            createddate=create_date_before_given_date(15, date_today),
            name="ServiceTest3",
            description="ServiceTestDescription",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate=create_date_after_given_date(7, create_date_before_given_date(15, date_today)),
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service3.save()

        # test period selection "all"
        field1 = "all"
        field2 = create_date_before_given_date(501, date_today)
        field3 = date_today
        period = make_query_for_service_list(field1, field2, field3)
        services = Service.objects.filter(createddate__gte=period["date_old"],
                                          createddate__lte=period["date_new"])
        service_count = services.count()
        print(service_count)
        self.assertEquals(service_count, 3)

        # test period selection "week"
        field1 = "week"
        field2 = create_date_before_given_date(501, date_today)
        field3 = date_today
        period = make_query_for_service_list(field1, field2, field3)
        services = Service.objects.filter(createddate__gte=period["date_old"],
                                          createddate__lte=period["date_new"])
        service_count = services.count()
        print(service_count)
        self.assertEquals(service_count, 1)

        # test period selection "month"
        field1 = "month"
        field2 = create_date_before_given_date(501, date_today)
        field3 = date_today
        period = make_query_for_service_list(field1, field2, field3)
        services = Service.objects.filter(createddate__gte=period["date_old"],
                                          createddate__lte=period["date_new"])
        service_count = services.count()
        print(service_count)
        self.assertEquals(service_count, 2)

        # test period selection "year"
        field1 = "year"
        field2 = create_date_before_given_date(501, date_today)
        field3 = date_today
        period = make_query_for_service_list(field1, field2, field3)
        services = Service.objects.filter(createddate__gte=period["date_old"],
                                          createddate__lte=period["date_new"])
        service_count = services.count()
        print(service_count)
        self.assertEquals(service_count, 2)

        # test period selection ""select""
        field1 = ""
        field2 = create_date_before_given_date(501, date_today)
        field3 = date_today
        period = make_query_for_service_list(field1, field2, field3)
        services = Service.objects.filter(createddate__gte=period["date_old"],
                                          createddate__lte=period["date_new"])
        service_count = services.count()
        print(service_count)
        self.assertEquals(service_count, 3)
