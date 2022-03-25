from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from social.models import Service, UserProfile, Event, ServiceApplication
from social.forms import ServiceForm, EventForm, ServiceApplicationForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.utils import timezone

class Index(View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.filter(isDeleted=False).order_by('-createddate')
        events = Event.objects.filter(isDeleted=False).order_by('-eventcreateddate')
        events_count = len(events)
        services_count = len(services)
        currentTime = timezone.now()
        context = {
            'services': services,
            'events': events,
            'services_count': services_count,
            'events_count': events_count,
            'currentTime': currentTime,
        }

        return render(request, 'landing/index.html', context)