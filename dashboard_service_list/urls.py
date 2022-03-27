from django.urls import path
from .views import list_services

urlpatterns = [

    path("servicelist/", list_services, name="servicelist"),

]
