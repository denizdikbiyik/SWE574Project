from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Service, Feedback, UserProfile, Event, ServiceApplication
from .forms import ServiceForm, EventForm, FeedbackForm, ServiceApplicationForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect

class ServiceCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ServiceForm()

        context = {
            'form': form,
        }

        return render(request, 'social/service_create.html', context)
    
    def post(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate')
        form = ServiceForm(request.POST, request.FILES)

        if form.is_valid():
            new_service = form.save(commit=False)
            new_service.creater = request.user
            new_service.save()

        context = {
            'service_list': services,
            'form': form,
        }

        return redirect('allservices')

class AllServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate')
        form = ServiceForm()

        context = {
            'services': services,
        }

        return render(request, 'social/allservices.html', context)

class CreatedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.filter(creater=request.user).order_by('-createddate')
        form = ServiceForm()

        context = {
            'services': services,
        }

        return render(request, 'social/createdservices.html', context)

class AppliedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.all()
        serviceapplications = ServiceApplication.objects.all()
        servicesapplied = []
        for serviceapplication in serviceapplications:
            for service in services:
                if serviceapplication.service == service:
                    if serviceapplication.applicant == request.user:
                        servicesapplied.append(service)

        form = ServiceForm()

        context = {
            'services': services,
            'serviceapplied': servicesapplied,
        }

        return render(request, 'social/appliedservices.html', context)

class ServiceDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        #form = ServiceForm()
        #form = FeedbackForm()
        applications = ServiceApplication.objects.filter(service=pk).order_by('-date')
        applications_this = applications.filter(applicant=request.user)
        number_of_accepted = len(applications.filter(approved=True))
        if len(applications) == 0:
            is_applied = False
            is_accepted = False
        for application in applications:
            if application.applicant == request.user:
                is_applied = True
                is_accepted = application.approved
                break
            else:
                is_applied = False
                is_accepted = False

        context = {
            'service': service,
            #'form': form,
            #'feedbacks': feedbacks,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_applied': is_applied,
            'applications_this': applications_this,
            'is_accepted': is_accepted,
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
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        form = ServiceApplicationForm(request.POST)
        applications = ServiceApplication.objects.filter(service=pk).order_by('-date')
        applications_this = applications.filter(applicant=request.user)
        number_of_accepted = len(applications.filter(approved=True))
        if len(applications) == 0:
            is_applied = False
        for application in applications:
            if application.applicant == request.user:
                is_applied = True
                break
            else:
                is_applied = False

        if form.is_valid():
            if is_applied == False:
                new_application = form.save(commit=False)
                new_application.applicant = request.user
                new_application.service = service
                new_application.approved = False
                new_application.save()

        context = {
            'service': service,
            'form': form,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_applied': is_applied,
            'applications_this': applications_this,
        }

        #return render(request, 'social/service_detail.html', context)
        return redirect('service-detail', pk=service.pk)

class ApplicationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ServiceApplication
    template_name = 'social/application_delete.html'

    def get_success_url(self):
        pk = self.kwargs['service_pk']
        return reverse_lazy('service-detail', kwargs={'pk': pk})
    
    def test_func(self):
        application = self.get_object()
        return self.request.user == application.applicant

class ApplicationEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ServiceApplication
    fields = ['approved']
    template_name = 'social/application_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['service_pk']
        return reverse_lazy('service-detail', kwargs={'pk': pk})
    
    def test_func(self):
        application = self.get_object()
        return self.request.user == application.service.creater

class ServiceEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Service
    fields = ['picture', 'name', 'description', 'servicedate', 'location', 'capacity', 'duration']
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
    success_url = reverse_lazy('allservices')

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

class EventCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = EventForm()

        context = {
            'form': form,
        }

        return render(request, 'social/event_create.html', context)
    
    def post(self, request, *args, **kwargs):
        events = Event.objects.all().order_by('-eventcreateddate')
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.eventcreater = request.user
            new_event.save()

        context = {
            'event_list': events,
            'form': form,
        }

        return redirect('allevents')

class AllEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.all().order_by('-eventcreateddate')
        form = EventForm()

        context = {
            'events': events,
        }

        return render(request, 'social/allevents.html', context)

class CreatedEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(eventcreater=request.user).order_by('-eventcreateddate')
        form = EventForm()

        context = {
            'events': events,
        }

        return render(request, 'social/createdevents.html', context)

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
    fields = ['eventpicture', 'eventname', 'eventdescription', 'eventdate', 'eventlocation', 'eventcapacity', 'eventduration']
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
    success_url = reverse_lazy('allevents')

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.eventcreater

class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        followers = profile.followers.all()
        if len(followers) == 0:
            is_following = False
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False
        number_of_followers = len(followers)
        context = {
            'user': user,
            'profile': profile,
            'number_of_followers': number_of_followers,
            'is_following': is_following
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

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        follow_pk = self.kwargs['followpk']
        profile = UserProfile.objects.get(pk=follow_pk)
        profile.followers.add(request.user)
        return redirect('profile', pk=follow_pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        follow_pk = self.kwargs['followpk']
        profile = UserProfile.objects.get(pk=follow_pk)
        profile.followers.remove(request.user)
        return redirect('profile', pk=follow_pk)

class RemoveMyFollower(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower_pk = self.kwargs['follower_pk']
        follower = UserProfile.objects.get(pk=follower_pk).user
        profile = UserProfile.objects.get(pk=request.user.pk)
        profile.followers.remove(follower)
        return redirect('followers', pk=request.user.pk)

class FollowersListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()
        number_of_followers = len(followers)
        context = {
            'followers': followers,
            'profile': profile,
            'number_of_followers': number_of_followers
        }

        return render(request, 'social/followers_list.html', context)


class TimeLine(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(pk=request.user.pk)
        allUsers = UserProfile.objects.all()
        followedOnes = []
        services2 = []
        events2 = []
        for auser in allUsers:
            thisFollowers = UserProfile.objects.get(pk=auser.pk).followers.all()
            if request.user in thisFollowers:
                followedOnes.append(auser)
        services = Service.objects.all().order_by('-createddate')
        events = Event.objects.all().order_by('-eventcreateddate')
        for one in followedOnes:
            for service in services:
                if service.creater == one.user :
                    services2.append(service)
            for event in events:
                if event.eventcreater == one.user :
                    events2.append(event)
        events_count = len(events2)
        services_count = len(services2)

        context = {
            'services': services2,
            'events': events2,
            'services_count': services_count,
            'events_count': events_count
        }

        return render(request, 'social/timeline.html', context)
    