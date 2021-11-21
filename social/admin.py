from django.contrib import admin
from .models import Service, Event, UserProfile
#from .models import Service, Event, Feedback, UserProfile

admin.site.register(Service)
admin.site.register(Event)
#admin.site.register(Feedback)
admin.site.register(UserProfile)