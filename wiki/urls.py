from django.urls import path
from .views import list_descriptions, list_interests, edit_descriptions

urlpatterns = [
    path("wiki/", list_descriptions, name="wiki"),
    path("wikiedit/<int:pk>", edit_descriptions, name="wikiedit"),
    path("wiki/interest", list_interests, name="wiki_interest")
]
