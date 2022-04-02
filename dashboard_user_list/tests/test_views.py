from django.http import HttpRequest
from django.test import TestCase, Client
from django.urls import reverse


from dashboard_user_list.views import make_context_for_username_list

from django.contrib.auth.models import User




class TestViews(TestCase):
    # P
    def test_url_accessible_by_name(self):
        client = Client()
        response = client.get(reverse("userlist"))
        self.assertEquals(response.status_code, 200)

    # P
    def test_view_uses_correct_template(self):
        client = Client()
        response = client.get(reverse("userlist"))
        self.assertTemplateUsed(response, "dashboard_user_list/userlist.html")

    # P
    def test_url_exists(self):
        client = Client()
        response = client.get("/dashboarduserlist/userlist/")
        self.assertEqual(response.status_code, 200)



        test_user1 = User.objects.create(

            username="Test_username1",
            date_joined='2022-04-01 10:00:00+03'

        )
        test_user1.save()



        test_user2 = User.objects.create(

            username="Test_username2",
            date_joined='2022-03-11 10:11:00+03'
        )
        test_user2.save()


        test_user3 = User.objects.create(

            username="Test_username3",
            date_joined='2022-02-11 10:11:00+03'
        )
        test_user3.save()

        # test period selection "all"
        field1 = "all"
        field2 = None
        field3 = "date_joined"
        context = make_context_for_username_list(field1, field2, field3)
        user_count = context["users"].count()
        print(context["users"].count())
        self.assertEquals(user_count, 3)

        # test period selection "week"
        field1 = "week"
        field2 = None
        field3 = "date_joined"
        context = make_context_for_username_list(field1, field2, field3)
        user_count = context["users"].count()
        print(context["users"].count())
        self.assertEquals(user_count, 1)

        # test period selection "month"
        field1 = "month"
        field2 = None
        field3 = "date_joined"
        context = make_context_for_username_list(field1, field2, field3)
        user_count = context["users"].count()
        print(context["users"].count())
        self.assertEquals(user_count, 2)

        # test period selection "select"
        field1 = "select"
        field2 = '2022-02-01'
        field3 = '2022-02-22'
        field4 = "date_joined"
        context = make_context_for_username_list(field1, field2, field3, field4)
        user_count = context["users"].count()
        print(context["users"].count())
        self.assertEquals(user_count, 1)


