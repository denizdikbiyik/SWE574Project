from django.urls import path
from .views import ServiceCreateView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventCreateView, \
    EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, \
    ApplicationDeleteView, ApplicationEditView, FollowersListView, RemoveMyFollower, TimeLine, AllServicesView, \
    AllEventsView, CreatedServicesView, CreatedEventsView, AppliedServicesView, ConfirmServiceTaken, \
    ConfirmServiceGiven, RateUser, RateUserDelete, RateUserEdit, ServiceSearch, EventSearch, Notifications, \
    EventApplicationDeleteView, AppliedEventsView, RequestCreateView, CreatedRequestsView, RequestsFromMeView, \
    RequestDetailView, RequestDeleteView, ServiceFilter, AllUsersView, UsersServicesListView, UsersEventsListView, \
    AddAdminView, RemoveAdminView, DashboardServiceDetailView

urlpatterns = [
    path('service/create', ServiceCreateView.as_view(), name='service-create'),
    path('service', AllServicesView.as_view(), name='allservices'),
    path('service/createdservices', CreatedServicesView.as_view(), name='createdservices'),
    path('service/appliedservices', AppliedServicesView.as_view(), name='appliedservices'),
    path('service/<int:pk>', ServiceDetailView.as_view(), name='service-detail'),
    path('service/edit/<int:pk>', ServiceEditView.as_view(), name='service-edit'),
    path('service/delete/<int:pk>', ServiceDeleteView.as_view(), name='service-delete'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('event/create', EventCreateView.as_view(), name='event-create'),
    path('event', AllEventsView.as_view(), name='allevents'),
    path('event/createdevents', CreatedEventsView.as_view(), name='createdevents'),
    path('event/<int:pk>', EventDetailView.as_view(), name='event-detail'),
    path('event/edit/<int:pk>', EventEditView.as_view(), name='event-edit'),
    path('event/delete/<int:pk>', EventDeleteView.as_view(), name='event-delete'),
    path('profile/<int:pk>/followers/add/<int:followpk>', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove/<int:followpk>', RemoveFollower.as_view(), name='remove-follower'),
    path('followers/remove/<int:follower_pk>', RemoveMyFollower.as_view(), name='remove-my-follower'),
    path('service/<int:service_pk>/application/delete/<int:pk>', ApplicationDeleteView.as_view(), name='application-delete'),
    path('service/<int:service_pk>/application/edit/<int:pk>/', ApplicationEditView.as_view(), name='application-edit'),
    path('service/<int:pk>/confirmtaken/', ConfirmServiceTaken.as_view(), name='confirm-service-taken'),
    path('service/<int:pk>/confirmgiven/', ConfirmServiceGiven.as_view(), name='confirm-service-given'),
    path('profile/<int:pk>/followers/', FollowersListView.as_view(), name='followers'),
    path('rate/<int:servicepk>/<int:ratedpk>', RateUser.as_view(), name='rateuser'),
    path('rate/edit/<int:pk>', RateUserEdit.as_view(), name='rating-edit'),
    path('rate/delete/<int:pk>', RateUserDelete.as_view(), name='rating-delete'),
    path('timeline', TimeLine.as_view(), name='timeline'),
    path('service-search', ServiceSearch.as_view(), name='service-search'),
    path('event-search', EventSearch.as_view(), name='event-search'),
    path('notifications', Notifications.as_view(), name='notifications'),
    path('event/<int:event_pk>/application/delete/<int:pk>', EventApplicationDeleteView.as_view(), name='event-application-delete'),
    path('event/appliedevents', AppliedEventsView.as_view(), name='appliedevents'),
    path('request/create', RequestCreateView.as_view(), name='request-create'),
    path('request/createdrequests', CreatedRequestsView.as_view(), name='createdrequests'),
    path('request/requestsfromme', RequestsFromMeView.as_view(), name='requestsfromme'),
    path('request/<int:pk>', RequestDetailView.as_view(), name='request-detail'),
    path('request/delete/<int:pk>', RequestDeleteView.as_view(), name='request-delete'),
    path('service-filter', ServiceFilter.as_view(), name='service-filter'),
    path('allusers', AllUsersView.as_view(), name='allusers'),

    path('profile/<int:pk>/services/', UsersServicesListView.as_view(), name='usersservices'),
    path('profile/<int:pk>/events/', UsersEventsListView.as_view(), name='usersevents'),

    path('profile/<int:pk>/admins/add/', AddAdminView.as_view(), name='add-admin'),
    path('profile/<int:pk>/admins/remove/', RemoveAdminView.as_view(), name='remove-admin'),

    path('dashboard/service/<int:pk>', DashboardServiceDetailView.as_view(), name='dashboard-service-detail')
]