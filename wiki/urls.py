from django.urls import path
from .views import list_descriptions, list_interests

urlpatterns = [
    path("wiki/", list_descriptions, name="wiki"),
    path("wiki/interest", list_interests, name="wiki_interest")
]
