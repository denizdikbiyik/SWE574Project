from django.contrib import admin
from .models import Service, Event, UserProfile, ServiceApplication

admin.site.register(Service)
admin.site.register(Event)
admin.site.register(UserProfile)
admin.site.register(ServiceApplication)