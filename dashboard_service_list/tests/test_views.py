from django.http import HttpRequest
from django.test import TestCase, Client
from django.urls import reverse

from dashboard_service_list.views import make_context_for_service_list
from social.models import Service
from django.contrib.auth.models import User


class TestViews(TestCase):
    # P
    def test_url_accessible_by_name(self):
        client = Client()
        response = client.get(reverse("servicelist"))
        self.assertEquals(response.status_code, 200)

    # P
    def test_view_uses_correct_template(self):
        client = Client()
        response = client.get(reverse("servicelist"))
        self.assertTemplateUsed(response, "dasboard_service_list/servicelist.html")

    # P
    def test_url_exists(self):
        client = Client()
        response = client.get("/dashboard/servicelist/")
        self.assertEqual(response.status_code, 200)

    def test_make_context_for_service_list(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        # 11.01.2020 / all
        test_service1 = Service.objects.create(
            creater=test_user1,
            createddate='2020-01-11 10:00:00+03',
            name="ServiceTest1",
            description="ServiceTestDescription",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-11 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service1.save()

        # 20.03.2022 all & month & week
        test_service2 = Service.objects.create(
            creater=test_user1,
            createddate='2022-03-20 10:00:00+03',
            name="ServiceTest2",
            description="ServiceTestDescription",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-11 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service2.save()

        # 15.03.2022 all & month
        test_service3 = Service.objects.create(
            creater=test_user1,
            createddate='2022-03-15 10:00:00+03',
            name="ServiceTest3",
            description="ServiceTestDescription",
            picture='uploads/service_pictures/default.png',
            location='41.0255493,28.9742571',
            servicedate='2030-01-11 10:00:00+03',
            capacity=1,
            duration=1,
            is_given=False,
            is_taken=False
        )
        test_service3.save()

        # test period selection "all"
        field1 = "all"
        field2 = None
        field3 = None
        field4 = "createddate"
        context = make_context_for_service_list(field1, field2, field3, field4)
        service_count = context["services"].count()
        print(context["services"].count())
        self.assertEquals(service_count, 3)

        # test period selection "week"
        field1 = "week"
        field2 = None
        field3 = None
        field4 = "createddate"
        context = make_context_for_service_list(field1, field2, field3, field4)
        service_count = context["services"].count()
        print(context["services"].count())
        self.assertEquals(service_count, 1)

        # test period selection "month"
        field1 = "month"
        field2 = None
        field3 = None
        field4 = "createddate"
        context = make_context_for_service_list(field1, field2, field3, field4)
        service_count = context["services"].count()
        print(context["services"].count())
        self.assertEquals(service_count, 2)

        # test period selection ""select""
        field1 = "select"
        field2 = '2020-01-10'
        field3 = '2020-01-12'
        field4 = "createddate"
        context = make_context_for_service_list(field1, field2, field3, field4)
        service_count = context["services"].count()
        print(context["services"].count())
        self.assertEquals(service_count, 1)
