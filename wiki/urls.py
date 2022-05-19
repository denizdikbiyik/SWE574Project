from django.urls import path
from .views import list_descriptions, list_interests, edit_service_descriptions, edit_event_descriptions

urlpatterns = [
    path("wiki/", list_descriptions, name="wiki"),
    path("wikiedit/<int:pk>", edit_service_descriptions, name="wikiedit"),
    path("wikieditevent/<int:pk>", edit_event_descriptions, name="wikieditevent"),
    path("wiki/interest", list_interests, name="wiki_interest")
]
