from django.contrib import admin
from .models import UserProfile, Service, Event, ServiceApplication, EventApplication, Tag, UserRatings, UserComplaints, NotifyUser, Log, Communication, Like, Featured, Interest, Search

admin.site.register(UserProfile)
admin.site.register(Service)
admin.site.register(Event)
admin.site.register(ServiceApplication)
admin.site.register(EventApplication)
admin.site.register(Tag)
admin.site.register(UserRatings)
admin.site.register(UserComplaints)
admin.site.register(NotifyUser)
admin.site.register(Log)
admin.site.register(Communication)
admin.site.register(Like)
admin.site.register(Featured)
admin.site.register(Interest)
admin.site.register(Search)