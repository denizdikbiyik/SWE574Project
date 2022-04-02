from django.urls import path
from .views import list_events

urlpatterns = [

    path("eventlist/", list_events, name="eventlist"),

]
