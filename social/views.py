from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Service, Feedback, UserProfile, Event, ServiceApplication
from .forms import ServiceForm, EventForm, FeedbackForm, ServiceApplicationForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone

class ServiceCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ServiceForm()

        context = {
            'form': form,
        }

        return render(request, 'social/service_create.html', context)
    
    def post(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate')
        creater_user_profile = UserProfile.objects.get(pk=request.user)
        form = ServiceForm(request.POST, request.FILES)

        if form.is_valid():
            totalcredit = creater_user_profile.reservehour + creater_user_profile.credithour
            new_service = form.save(commit=False)
            if totalcredit + new_service.duration <= 15:
                new_service.creater = request.user
                creater_user_profile.reservehour = creater_user_profile.reservehour + new_service.duration
                creater_user_profile.save()
                new_service.save()
                messages.success(request, 'Service creation is successful.')
            else:
                messages.warning(request, 'You cannot create this service which causes credit hours exceed 15.')

        context = {
            'service_list': services,
            'form': form,
        }

        return render(request, 'social/service_create.html', context)

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
        number_of_createdservice = len(services)

        context = {
            'services': services,
            'number_of_createdservice': number_of_createdservice,
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
        number_of_appliedservice = len(servicesapplied)

        form = ServiceForm()

        context = {
            'services': services,
            'serviceapplied': servicesapplied,
            'number_of_appliedservice': number_of_appliedservice,
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
        accepted_applications = applications.filter(approved=True)
        application_number = len(applications)
        is_active = True
        if service.servicedate <= timezone.now():
            is_active = False
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
            'is_active': is_active,
            'application_number': application_number,
            'accepted_applications': accepted_applications
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
        applicant_user_profile = UserProfile.objects.get(pk=request.user)
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
                totalcredit = applicant_user_profile.reservehour + applicant_user_profile.credithour
                if totalcredit > service.duration:
                    new_application = form.save(commit=False)
                    new_application.applicant = request.user
                    new_application.service = service
                    new_application.approved = False
                    new_application.save()
                    applicant_user_profile.reservehour = applicant_user_profile.reservehour - service.duration
                    applicant_user_profile.save()
                else:
                    messages.warning(request, 'You do not have enough credit to apply.')

        context = {
            'service': service,
            'form': form,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_applied': is_applied,
            'applications_this': applications_this,
        }

        return redirect('service-detail', pk=service.pk)

class ApplicationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ServiceApplication
    template_name = 'social/application_delete.html'

    def get_success_url(self):
        service_pk = self.kwargs['service_pk']
        service = Service.objects.get(pk=service_pk)
        application = self.get_object()
        applicant_user_profile = UserProfile.objects.get(pk=application.applicant.pk)
        applicant_user_profile.reservehour = applicant_user_profile.reservehour + service.duration
        applicant_user_profile.save()
        return reverse_lazy('service-detail', kwargs={'pk': service_pk})
    
    def test_func(self):
        application = self.get_object()
        isOK = False
        if self.request.user == application.applicant:
            isOK = True
        if self.request.user == application.service.creater:
            isOK = True
        return isOK

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

class ConfirmServiceTaken(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        service.is_taken = True
        service.save()
        CreditExchange(service)
        return redirect('service-detail', pk=pk)

class ConfirmServiceGiven(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        service.is_given = True
        service.save()
        CreditExchange(service)
        return redirect('service-detail', pk=pk)
    
def CreditExchange(service):
    applications = ServiceApplication.objects.filter(service=service.pk).filter(approved=True)
    if service.is_taken == True:
        if service.is_given == True:
            service_giver = UserProfile.objects.get(pk=service.creater.pk)
            service_giver.credithour = service_giver.credithour + service.duration
            service_giver.reservehour = service_giver.reservehour - service.duration
            service_giver.save()
            for application in applications:
                service_taker = UserProfile.objects.get(pk=application.applicant.pk)
                service_taker.credithour = service_taker.credithour - service.duration
                service_taker.reservehour = service_taker.reservehour + service.duration
                service_taker.save()
    return redirect('service-detail', pk=service.pk)

class ServiceEditView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        service = Service.objects.get(pk=pk)

        if service.creater == request.user:
            if service.servicedate > timezone.now():
                form = ServiceForm(instance = service)
                context = {
                    'form': form,
                }

                return render(request, 'social/service_edit.html', context)
            else:
                return redirect('service-detail', pk=service.pk)
        
        else:
            return redirect('service-detail', pk=service.pk)

    def post(self, request, *args, pk, **kwargs):
        form = ServiceForm(request.POST, request.FILES)
        service = Service.objects.get(pk=pk)

        if form.is_valid():
            service_creater_profile = UserProfile.objects.get(pk=service.creater)
            applications = ServiceApplication.objects.filter(service=service)
            totalcredit = service_creater_profile.reservehour + service_creater_profile.credithour - service.duration
            edit_service = form.save(commit=False)
            if totalcredit + edit_service.duration <= 15:

                service_creater_profile.reservehour = service_creater_profile.reservehour - service.duration + edit_service.duration
                service_creater_profile.save()
                for application in applications:
                    service_applicant_profile = UserProfile.objects.get(pk=application.applicant)
                    service_applicant_profile.reservehour = service_applicant_profile.reservehour + service.duration - edit_service.duration
                    service_applicant_profile.save()
                
                service.picture = service.picture
                if request.FILES:
                    service.picture = edit_service.picture
                service.name = edit_service.name
                service.description = edit_service.description
                service.servicedate = edit_service.servicedate
                service.location = edit_service.location
                service.capacity = edit_service.capacity
                service.duration = edit_service.duration

                service.save()
                
                messages.success(request, 'Service editing is successful.')
            else:
                messages.warning(request, 'You cannot make this service which causes credit hours exceed 15.')
        
        context = {
            'form': form,
        }

        return render(request, 'social/service_edit.html', context)



    # model = Service
    # fields = ['picture', 'name', 'description', 'servicedate', 'location', 'capacity', 'duration']
    # template_name = 'social/service_edit.html'
    
    # def get_success_url(self):
    #     pk = self.kwargs['pk']
    #     return reverse_lazy('service-detail', kwargs={'pk': pk})
    
    # def test_func(self):
    #     service = self.get_object()
    #     return self.request.user == service.creater

class ServiceDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        service = Service.objects.get(pk=pk)

        if service.creater == request.user:
            if service.servicedate > timezone.now():
                form = ServiceForm(instance = service)
                context = {
                    'form': form,
                }

                return render(request, 'social/service_delete.html', context)
            else:
                return redirect('service-detail', pk=service.pk)
        
        else:
            return redirect('service-detail', pk=service.pk)

    def post(self, request, *args, pk, **kwargs):
        service = Service.objects.get(pk=pk)
        service.creater = request.user
        service_creater_profile = UserProfile.objects.get(pk=service.creater)
        service_creater_profile.reservehour = service_creater_profile.reservehour - service.duration
        service_creater_profile.save()
        applications = ServiceApplication.objects.filter(service=service)
        for application in applications:
            service_applicant_profile = UserProfile.objects.get(pk=application.applicant)
            service_applicant_profile.reservehour = service_applicant_profile.reservehour + service.duration
            service_applicant_profile.save()

        service.delete()
        return redirect('allservices')

    # model = Service
    # template_name = 'social/service_delete.html'
    # success_url = reverse_lazy('allservices')

    # def test_func(self):
    #     service = self.get_object()
    #     isOK = False
    #     if self.request.user == service.creater:
    #         isOK = True      
    #         service_creater_profile = UserProfile.objects.get(pk=service.creater)
    #         service_creater_profile.reservehour = service_creater_profile.reservehour - service.duration
    #         service_creater_profile.save()
    #         applications = ServiceApplication.objects.filter(service=service)
    #         for application in applications:
    #             service_applicant_profile = UserProfile.objects.get(pk=application.applicant)
    #             service_applicant_profile.reservehour = service_applicant_profile.reservehour + service.duration
    #             service_applicant_profile.save()
    #     else:
    #         isOK = False
    #     return isOK

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
            messages.success(request, 'Event creation is successful.')

        context = {
            'event_list': events,
            'form': form,
        }

        return render(request, 'social/event_create.html', context)

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
        number_of_createdevent = len(events)
        form = EventForm()

        context = {
            'events': events,
            'number_of_createdevent': number_of_createdevent,
        }

        return render(request, 'social/createdevents.html', context)

class EventDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        form = EventForm()
        is_active = True
        if event.eventdate <= timezone.now():
            is_active = False

        context = {
            'event': event,
            'form': form,
            'is_active': is_active,
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
    