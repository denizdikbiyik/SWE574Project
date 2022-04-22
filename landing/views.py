from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from social.models import Service, UserProfile, Event, ServiceApplication, Featured
from social.forms import ServiceForm, EventForm, ServiceApplicationForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
from online_users.models import OnlineUserActivity

class Index(View):
    def get(self, request, *args, **kwargs):
        currentTime = timezone.now()
        services = []
        events = []
        featured_services = []
        featured_events = []

        featuredServicesList = Featured.objects.filter(itemType="service")
        for featuredServiceList in featuredServicesList:
            serviceFeatured = Service.objects.get(pk=featuredServiceList.itemId)
            featured_services.append(serviceFeatured)
        featured_services_count = len(featured_services)
        featuredEventsList = Featured.objects.filter(itemType="event")
        for featuredEventList in featuredEventsList:
            eventFeatured = Event.objects.get(pk=featuredEventList.itemId)
            featured_events.append(eventFeatured)
        featured_events_count = len(featured_events)

        servicesToGet = Service.objects.filter(isDeleted=False).filter(isActive=True).filter(servicedate__gte=currentTime).order_by('-createddate')
        for serviceToGet in servicesToGet:
            if serviceToGet not in featured_services:
                services.append(serviceToGet)
        services_count = len(services)
        eventsToGet = Event.objects.filter(isDeleted=False).filter(isActive=True).filter(eventdate__gte=currentTime).order_by('-eventcreateddate')
        for eventToGet in eventsToGet:
            if eventToGet not in featured_events:
                events.append(eventToGet)
        events_count = len(events)
        
        context = {
            'services': services,
            'events': events,
            'services_count': services_count,
            'events_count': events_count,
            'featured_services': featured_services,
            'featured_events': featured_events,
            'featured_services_count': featured_services_count,
            'featured_events_count': featured_events_count,
            'currentTime': currentTime,
        }

        return render(request, 'landing/index.html', context)