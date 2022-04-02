import datetime

from django.http import HttpRequest
from django.test import TestCase, Client
from django.urls import reverse
import datetime
from dashboard_event_list.views import make_context_for_event_list
from social.models import Event
from django.contrib.auth.models import User


class TestViews(TestCase):
    '''
    # P
    def test_url_accessible_by_name(self):
        client = Client()
        response = client.get(reverse("eventlist"))
        self.assertEquals(response.status_code, 404)

    # P
    def test_view_uses_correct_template(self):
        client = Client()
        response = client.get(reverse("eventlist"))
        self.assertTemplateUsed(response, "dashboard_event_list/eventlist.html")

    # P
    def test_url_exists(self):
        client = Client()
        response = client.get("/dashboardevent/eventlist/")
        self.assertEqual(response.status_code, 404)
    '''

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
        test_service1 = Event.objects.create(
            eventcreater=test_user1,
            eventcreateddate=create_date_before_given_date(500, date_today),
            eventname="ServiceTest1",
            eventdescription="ServiceTestDescription",
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate=create_date_after_given_date(7, create_date_before_given_date(500, date_today)),
            eventcapacity=1,
            eventduration=1,
        )
        test_service1.save()

        # 2. included only in all & month & week
        test_service2 = Event.objects.create(
            eventcreater=test_user1,
            eventcreateddate=create_date_before_given_date(2, date_today),
            eventname="ServiceTest1",
            eventdescription="ServiceTestDescription",
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate=create_date_after_given_date(7, create_date_before_given_date(500, date_today)),
            eventcapacity=1,
            eventduration=1,
        )
        test_service2.save()

        # 3. included only in all & month
        test_service3 = Event.objects.create(
            eventcreater=test_user1,
            eventcreateddate=create_date_before_given_date(15, date_today),
            eventname="ServiceTest1",
            eventdescription="ServiceTestDescription",
            eventpicture='uploads/service_pictures/default.png',
            eventlocation='41.0255493,28.9742571',
            eventdate=create_date_after_given_date(7, create_date_before_given_date(500, date_today)),
            eventcapacity=1,
            eventduration=1,
        )
        test_service3.save()

        # test period selection "all"
        field1 = "all"
        field2 = None
        field3 = None
        field4 = "createddate"
        context = make_context_for_event_list(field1, field2, field3, field4)
        event_count = context["events"].count()
        print(context["events"].count())
        self.assertEquals(event_count, 3)

        # test period selection "week"
        field1 = "week"
        field2 = None
        field3 = None
        field4 = "createddate"
        context = make_context_for_event_list(field1, field2, field3, field4)
        event_count = context["events"].count()
        print(context["events"].count())
        self.assertEquals(event_count, 1)

        # test period selection "month"
        field1 = "month"
        field2 = None
        field3 = None
        field4 = "createddate"
        context = make_context_for_event_list(field1, field2, field3, field4)
        event_count = context["events"].count()
        print(context["events"].count())
        self.assertEquals(event_count, 2)

        # test period selection ""select""
        field1 = "select"
        field2 = create_date_before_given_date(501, date_today)
        field3 = date_today
        field4 = "createddate"
        context = make_context_for_event_list(field1, field2, field3, field4)
        event_count = context["events"].count()
        print(context["events"].count())
        self.assertEquals(event_count, 3)
