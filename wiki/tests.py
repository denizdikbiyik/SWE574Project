from django.test import TestCase, Client
from django.urls import reverse

from social.models import Service, UserProfile, Event, ServiceApplication, UserRatings, NotifyUser, EventApplication, Tag, Log
from social.forms import ServiceForm, EventForm, ServiceApplicationForm, RatingForm, EventApplicationForm, ProfileForm, RequestForm
from social.views import ServiceCreateView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventCreateView, EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, ApplicationDeleteView, ApplicationEditView, FollowersListView, RemoveMyFollower, TimeLine, AllServicesView, AllEventsView, CreatedServicesView, CreatedEventsView, AppliedServicesView, ConfirmServiceTaken, ConfirmServiceGiven, RateUser, RateUserDelete, RateUserEdit, ServiceSearch, EventSearch, Notifications, EventApplicationDeleteView, AppliedEventsView, RequestCreateView, CreatedRequestsView, RequestsFromMeView, RequestDetailView, RequestDeleteView, ServiceFilter, AllUsersView, UsersServicesListView, UsersEventsListView, AddAdminView, RemoveAdminView
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from datetime import datetime


class TestViews(TestCase):
    def test_view_url_exists_at_desired_location(self):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user1.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')

        response = self.client.get(reverse('wiki'))
        self.assertEqual(response.status_code, 200)
