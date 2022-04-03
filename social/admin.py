from django.contrib import admin
from .models import Service, Event, UserProfile, ServiceApplication, EventApplication, Communication, Tag, NotifyUser, UserRatings

admin.site.register(Service)
admin.site.register(Event)
admin.site.register(UserProfile)
admin.site.register(ServiceApplication)
admin.site.register(EventApplication)
admin.site.register(UserRatings)
admin.site.register(Tag)
admin.site.register(Communication)
admin.site.register(NotifyUser)