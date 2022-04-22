from django.urls import path
from .views import list_descriptions

urlpatterns = [

    path("wiki/", list_descriptions, name="wiki")

]
