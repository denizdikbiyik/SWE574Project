from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from social.models import Service, Feedback, UserProfile, Event, ServiceApplication
from social.forms import ServiceForm, EventForm, FeedbackForm, ServiceApplicationForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect

class Index(View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate')
        events = Event.objects.all().order_by('-eventcreateddate')
        events_count = len(events)
        services_count = len(services)

        context = {
            'services': services,
            'events': events,
            'services_count': services_count,
            'events_count': events_count,
        }

        return render(request, 'landing/index.html', context)