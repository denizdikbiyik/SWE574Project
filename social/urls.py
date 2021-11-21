from django.urls import path
from .views import ServiceListView, ServiceDetailView, ServiceEditView, ServiceDeleteView
#from .views import ServiceListView, ServiceDetailView, ServiceEditView, ServiceDeleteView, FeedbackDeleteView

urlpatterns = [
    path('', ServiceListView.as_view(), name='service-list'),
    path('service/<int:pk>', ServiceDetailView.as_view(), name='service-detail'),
    path('service/edit/<int:pk>', ServiceEditView.as_view(), name='service-edit'),
    path('service/delete/<int:pk>', ServiceDeleteView.as_view(), name='service-delete'),
    #path('service/<int:service_pk>/feedback/delete/<int:pk>', FeedbackDeleteView.as_view(), name='feedback-delete'),
]