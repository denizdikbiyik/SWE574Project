from django.urls import path
from .views import list_users

urlpatterns = [

    #path("userlist/", list_users, name="userlist"),
    path('userlist/', list_users, name="userlist")
]
