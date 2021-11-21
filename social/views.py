from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Service, Feedback, UserProfile, Event
from .forms import ServiceForm, EventForm, FeedbackForm
from django.views.generic.edit import UpdateView, DeleteView

class ServiceListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate')
        form = ServiceForm()

        context = {
            'service_list': services,
            'form': form,
        }

        return render(request, 'social/service_list.html', context)
    
    def post(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate')
        form = ServiceForm(request.POST)

        if form.is_valid():
            new_service = form.save(commit=False)
            new_service.creater = request.user
            new_service.save()

        context = {
            'service_list': services,
            'form': form,
        }

        return render(request, 'social/service_list.html', context)

class ServiceDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        form = ServiceForm()
        #form = FeedbackForm()

        context = {
            'service': service,
            'form': form,
            #'feedbacks': feedbacks,
        }

        return render(request, 'social/service_detail.html', context)

    def post(self, request, *args, **kwargs):
        pass
    """
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        form = FeedbackForm(request.POST)

        if form.is_valid():
            new_feedback = form.save(commit=False)
            new_feedback.creater = request.user
            new_feedback.service = service
            new_feedback.save()
        
        feedbacks = Feedback.objects.filter(service=service).order_by('-createddate')

        context = {
            'service': service,
            'form': form,
            'feedbacks': feedbacks,
        }

        return render(request, 'social/service_detail.html', context)
    """

class ServiceEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Service
    fields = ['description']
    template_name = 'social/service_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('service-detail', kwargs={'pk': pk})
    
    def test_func(self):
        service = self.get_object()
        return self.request.user == service.creater

class ServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Service
    template_name = 'social/service_delete.html'
    success_url = reverse_lazy('service-list')

    def test_func(self):
        service = self.get_object()
        return self.request.user == service.creater

"""
class FeedbackDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Feedback
    template_name = 'social/feedback_delete.html'

    def get_success_url(self):
        pk = self.kwargs['service_pk']
        return reverse_lazy('service-detail', kwargs={'pk': pk})
    
    def test_func(self):
        service = self.get_object()
        return self.request.user == service.creater
"""

class EventListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.all().order_by('-eventcreateddate')
        form = EventForm()

        context = {
            'event_list': events,
            'form': form,
        }

        return render(request, 'social/event_list.html', context)
    
    def post(self, request, *args, **kwargs):
        events = Event.objects.all().order_by('-eventcreateddate')
        form = EventForm(request.POST)

        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.eventcreater = request.user
            new_event.save()

        context = {
            'event_list': events,
            'form': form,
        }

        return render(request, 'social/event_list.html', context)

class EventDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        form = EventForm()

        context = {
            'event': event,
            'form': form,
        }

        return render(request, 'social/event_detail.html', context)

    def post(self, request, *args, **kwargs):
        pass

class EventEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    fields = ['eventpicture', 'eventname', 'eventdescription', 'eventdate', 'eventlocation', 'eventcapacity']
    template_name = 'social/event_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('event-detail', kwargs={'pk': pk})
    
    def test_func(self):
        event = self.get_object()
        return self.request.user == event.eventcreater

class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'social/event_delete.html'
    success_url = reverse_lazy('event-list')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.eventcreater

class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        services = Service.objects.filter(creater=user).order_by('-createddate')

        context = {
            'user': user,
            'profile': profile,
            'services': services,
        }
        return render(request, 'social/profile.html', context)

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['name', 'bio', 'birth_date', 'location', 'picture']
    template_name = 'social/profile_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})
    
    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user