from django.urls import path
from .views import ServiceListView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventListView, EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView
#from .views import ServiceListView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventListView, EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, FeedbackDeleteView

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
]