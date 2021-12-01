from django.urls import path
from .views import ServiceListView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventListView, EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, ApplicationDeleteView, ApplicationEditView, FollowersListView, RemoveMyFollower
#from .views import ServiceListView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventListView, EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, FeedbackDeleteView, AddFollower, RemoveFollower, ApplicationDeleteView, ApplicationEditView, FollowersListView, RemoveMyFollower

urlpatterns = [
    path('service', ServiceListView.as_view(), name='service-list'),
    path('service/<int:pk>', ServiceDetailView.as_view(), name='service-detail'),
    path('service/edit/<int:pk>', ServiceEditView.as_view(), name='service-edit'),
    path('service/delete/<int:pk>', ServiceDeleteView.as_view(), name='service-delete'),
    #path('service/<int:service_pk>/feedback/delete/<int:pk>', FeedbackDeleteView.as_view(), name='feedback-delete'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('event', EventListView.as_view(), name='event-list'),
    path('event/<int:pk>', EventDetailView.as_view(), name='event-detail'),
    path('event/edit/<int:pk>', EventEditView.as_view(), name='event-edit'),
    path('event/delete/<int:pk>', EventDeleteView.as_view(), name='event-delete'),
    path('profile/<int:pk>/followers/add/<int:followpk>', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove/<int:followpk>', RemoveFollower.as_view(), name='remove-follower'),
    path('followers/remove/<int:follower_pk>', RemoveMyFollower.as_view(), name='remove-my-follower'),
    path('service/<int:service_pk>/application/delete/<int:pk>', ApplicationDeleteView.as_view(), name='application-delete'),
    path('service/<int:service_pk>/application/edit/<int:pk>/', ApplicationEditView.as_view(), name='application-edit'),
    path('profile/<int:pk>/followers/', FollowersListView.as_view(), name='followers'),
]