from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Service, UserProfile, Event, ServiceApplication, UserRatings, NotifyUser, EventApplication, Tag, Log, Communication
from .forms import ServiceForm, EventForm, ServiceApplicationForm, RatingForm, EventApplicationForm, ProfileForm, RequestForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Q

class ServiceCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ServiceForm()
        context = {
            'form': form,
        }
        return render(request, 'social/service_create.html', context)
    
    def post(self, request, *args, **kwargs):
        services = Service.objects.filter(isDeleted=False).order_by('-createddate')
        creater_user_profile = UserProfile.objects.get(pk=request.user)
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            totalcredit = creater_user_profile.reservehour + creater_user_profile.credithour
            new_service = form.save(commit=False)
            if totalcredit + new_service.duration <= 15:
                sameDateServices = Service.objects.filter(creater=request.user).filter(servicedate=new_service.servicedate).filter(isDeleted=False)
                sameDateEvents = Event.objects.filter(eventcreater=request.user).filter(eventdate=new_service.servicedate).filter(isDeleted=False)
                if len(sameDateServices) > 0 or  len(sameDateEvents) > 0:
                    messages.warning(request, 'You cannot create this service because you have one with the same datetime.')
                else:
                    new_service.creater = request.user
                    creater_user_profile.reservehour = creater_user_profile.reservehour + new_service.duration
                    creater_user_profile.save()
                    if new_service.category:
                        notification = NotifyUser.objects.create(notify=new_service.category.requester, notification=str(request.user)+' created service with your request '+str(new_service.category)+'.', offerType="request", offerPk=0)
                        notified_user = UserProfile.objects.get(pk=new_service.category.requester)
                        notified_user.unreadcount = notified_user.unreadcount+1
                        notified_user.save()
                    new_service.save()
                    messages.success(request, 'Service creation is successful.')
                    log = Log.objects.create(operation="createservice", itemType="service", itemId=new_service.pk, userId=request.user)
            else:
                messages.warning(request, 'You cannot create this service which causes credit hours exceed 15.')
        context = {
            'service_list': services,
            'form': form,
        }
        return render(request, 'social/service_create.html', context)

class AllServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.all().order_by('-createddate').filter(isDeleted=False)
        alltags = Tag.objects.all()
        form = ServiceForm()
        services_count = len(services)
        currentTime = timezone.now()
        context = {
            'services': services,
            'services_count': services_count,
            'currentTime': currentTime,
            'alltags': alltags,
        }
        return render(request, 'social/allservices.html', context)

class CreatedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.filter(creater=request.user).filter(isDeleted=False).order_by('-createddate')
        form = ServiceForm()
        number_of_createdservice = len(services)
        currentTime = timezone.now()
        context = {
            'services': services,
            'number_of_createdservice': number_of_createdservice,
            'currentTime': currentTime,
        }
        return render(request, 'social/createdservices.html', context)

class AppliedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.filter(isDeleted=False)
        serviceapplications = ServiceApplication.objects.all()
        servicesapplied = []
        for serviceapplication in serviceapplications:
            for service in services:
                if serviceapplication.service == service:
                    if serviceapplication.applicant == request.user:
                        servicesapplied.append(service)
        number_of_appliedservice = len(servicesapplied)
        form = ServiceForm()
        currentTime = timezone.now()
        context = {
            'services': services,
            'serviceapplied': servicesapplied,
            'number_of_appliedservice': number_of_appliedservice,
            'currentTime': currentTime,
        }
        return render(request, 'social/appliedservices.html', context)

class ServiceDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        notifications = NotifyUser.objects.filter(notify=request.user).filter(offerType="service").filter(offerPk=pk).filter(hasRead=False)
        countNotifications = len(notifications)
        for notification in notifications:
            notification.hasRead = True
            notification.save()
        userNotified = UserProfile.objects.get(pk=request.user.profile)
        userNotified.unreadcount = userNotified.unreadcount - countNotifications
        userNotified.save()
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
        allCommunications = Communication.objects.filter(itemType="service").filter(itemId=service.pk)
        allCommunicationsLength = len(allCommunications)
        context = {
            'service': service,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_applied': is_applied,
            'applications_this': applications_this,
            'is_accepted': is_accepted,
            'is_active': is_active,
            'application_number': application_number,
            'accepted_applications': accepted_applications,
            'allCommunications': allCommunications,
            'allCommunicationsLength': allCommunicationsLength
        }
        return render(request, 'social/service_detail.html', context)

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
                oldApplications = ServiceApplication.objects.filter(applicant=request.user).filter(approved=False)
                for oldApplication in oldApplications:
                    if oldApplication.service.servicedate <= timezone.now() and oldApplication.service.is_given == False and oldApplication.service.is_taken == False:
                        applicant_user_profile.reservehour = applicant_user_profile.reservehour + oldApplication.service.duration
                        oldApplication.service.is_given = True
                        oldApplication.service.is_taken = True
                        oldApplication.save()
                oldServices = Service.objects.filter(creater=request.user).filter(is_given=False).filter(is_taken=False).filter(isDeleted=False)
                applicationsForOldServiceCheck = ServiceApplication.objects.all()
                for oldService in oldServices:
                    if oldService.servicedate <= timezone.now():
                        if len(applicationsForOldServiceCheck.filter(service=oldService)) == 0 or len(applicationsForOldServiceCheck.filter(service=oldService).filter(approved=True)) == 0:
                            applicant_user_profile.reservehour = applicant_user_profile.reservehour - oldService.duration
                            oldService.is_taken = True
                            oldService.is_given = True
                            oldService.save()
                totalcredit = applicant_user_profile.reservehour + applicant_user_profile.credithour
                if totalcredit >= service.duration:
                    new_application = form.save(commit=False)
                    new_application.applicant = request.user
                    new_application.service = service
                    new_application.approved = False
                    new_application.save()
                    log = Log.objects.create(operation="createserviceapplication", itemType="service", itemId=service.pk, userId=request.user)
                    applicant_user_profile.reservehour = applicant_user_profile.reservehour - service.duration
                    applicant_user_profile.save()
                    notification = NotifyUser.objects.create(notify=service.creater, notification=str(new_application.applicant)+' applied to service '+str(new_application.service.name), offerType="service", offerPk=new_application.service.pk)
                    notified_user = UserProfile.objects.get(pk=service.creater)
                    notified_user.unreadcount = notified_user.unreadcount+1
                    notified_user.save()
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
        notification = NotifyUser.objects.create(notify=service.creater, notification=str(applicant_user_profile.user.username)+' canceled application for service '+str(service.name), offerType="service", offerPk=service.pk)
        notified_user = UserProfile.objects.get(pk=service.creater)
        notified_user.unreadcount = notified_user.unreadcount+1
        notified_user.save()
        log = Log.objects.create(operation="deleteserviceapplication", itemType="service", itemId=service.pk, affectedItemType="user", affectedItemId=application.applicant.pk, userId=self.request.user)
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
        application = self.get_object()
        notification = NotifyUser.objects.create(notify=application.applicant, notification='Your application status for '+str(application.service.name)+' is changed by the owner.', offerType="service", offerPk=application.service.pk)
        notified_user = UserProfile.objects.get(pk=application.applicant)
        notified_user.unreadcount = notified_user.unreadcount+1
        notified_user.save()
        log = Log.objects.create(operation="editserviceapplication", itemType="service", itemId=application.service.pk, affectedItemType="user", affectedItemId=application.applicant.pk, userId=self.request.user)
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
        applications = ServiceApplication.objects.filter(service=pk).filter(approved=True)
        for application in applications:
            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(service.name)+' taken confirmation done.', offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount+1
            notified_user.save()
        notification = NotifyUser.objects.create(notify=service.creater, notification=str(service.name)+' taken confirmation done.', offerType="service", offerPk=service.pk)
        notified_user = UserProfile.objects.get(pk=service.creater)
        notified_user.unreadcount = notified_user.unreadcount+1
        notified_user.save()
        log = Log.objects.create(operation="confirmtaken", itemType="service", itemId=service.pk, userId=request.user)
        return redirect('service-detail', pk=pk)

class ConfirmServiceGiven(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        service.is_given = True
        service.save()
        CreditExchange(service)
        applications = ServiceApplication.objects.filter(service=pk).filter(approved=True)
        for application in applications:
            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(service.name)+' given confirmation done.', offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount+1
            notified_user.save()
        log = Log.objects.create(operation="confirmgiven", itemType="service", itemId=service.pk, userId=request.user)
        return redirect('service-detail', pk=pk)
    
def CreditExchange(service):
    applications = ServiceApplication.objects.filter(service=service.pk).filter(approved=True)
    notConfirmedApplications = ServiceApplication.objects.filter(service=service.pk).filter(approved=False)
    if service.is_taken == True:
        if service.is_given == True:
            service_giver = UserProfile.objects.get(pk=service.creater.pk)
            service_giver.credithour = service_giver.credithour + service.duration
            service_giver.reservehour = service_giver.reservehour - service.duration
            service_giver.save()
            log1 = Log.objects.create(operation="earncredit", itemType="service", itemId=service.pk, affectedItemType="user", affectedItemId=service.creater.pk, userId=service.creater)
            for application in applications:
                service_taker = UserProfile.objects.get(pk=application.applicant.pk)
                service_taker.credithour = service_taker.credithour - service.duration
                service_taker.reservehour = service_taker.reservehour + service.duration
                service_taker.save()
                log2 = Log.objects.create(operation="spentcredit", itemType="service", itemId=service.pk, affectedItemType="user", affectedItemId=application.applicant.pk, userId=application.applicant)
            for notApplication in notConfirmedApplications:
                applicant = UserProfile.objects.get(pk=notApplication.applicant.pk)
                applicant.reservehour = applicant.reservehour + service.duration
                applicant.save()
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
                applications = ServiceApplication.objects.filter(service=service)
                number_of_accepted = len(applications.filter(approved=True))
                if edit_service.capacity < number_of_accepted:
                    messages.warning(request, 'You cannot make capacity below the accepted number, please remove accepted participants.')
                else:
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
                    service.category = edit_service.category
                    service.save()
                    log = Log.objects.create(operation="editservice", itemType="service", itemId=service.pk, userId=request.user)
                    messages.success(request, 'Service editing is successful.')
                    applications = ServiceApplication.objects.filter(service=service)
                    for application in applications:
                        notification = NotifyUser.objects.create(notify=application.applicant, notification=str(service.name)+' which you applied is edited.', offerType="service", offerPk=service.pk)
                        notified_user = UserProfile.objects.get(pk=application.applicant)
                        notified_user.unreadcount = notified_user.unreadcount+1
                        notified_user.save()
            else:
                messages.warning(request, 'You cannot make this service which causes credit hours exceed 15.')
        context = {
            'form': form,
        }
        return render(request, 'social/service_edit.html', context)

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
            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(service.name)+' service which you applied is deleted.', offerType="service")
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount+1
            notified_user.save()
            notificationsToChange = NotifyUser.objects.filter(notify=application.applicant).filter(hasRead=False).filter(offerType="service").filter(offerPk=pk)
            for notificationChange in notificationsToChange:
                notificationChange.offerPk = 0
                notificationChange.save()
            log1 = Log.objects.create(operation="deleteserviceapplication", itemType="service", itemId=service.pk, affectedItemType="user", affectedItemId=application.applicant.pk, userId=request.user)
            application.delete()
        log2 = Log.objects.create(operation="deleteservice", itemType="service", itemId=service.pk, userId=request.user)
        service.isDeleted = True
        ratingsToEdit = UserRatings.objects.filter(service=service)
        for ratingToEdit in ratingsToEdit:
            ratingToEdit.service = None
            ratingToEdit.save()
        service.save()
        return redirect('allservices')

class EventCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = EventForm()
        context = {
            'form': form,
        }
        return render(request, 'social/event_create.html', context)
    
    def post(self, request, *args, **kwargs):
        events = Event.objects.filter(isDeleted=False).order_by('-eventcreateddate')
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            new_event = form.save(commit=False)
            sameDateEvents = Event.objects.filter(eventcreater=request.user).filter(eventdate=new_event.eventdate).filter(isDeleted=False)
            sameDateServices = Service.objects.filter(creater=request.user).filter(servicedate=new_event.eventdate).filter(isDeleted=False)
            if len(sameDateEvents) > 0 or len(sameDateServices) > 0:
                messages.warning(request, 'You cannot create this event because you have one with the same datetime.')
            else:
                new_event.eventcreater = request.user
                new_event.save()
                log = Log.objects.create(operation="createevent", itemType="event", itemId=new_event.pk, userId=request.user)
                messages.success(request, 'Event creation is successful.')
        context = {
            'event_list': events,
            'form': form,
        }
        return render(request, 'social/event_create.html', context)

class AllEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(isDeleted=False).order_by('-eventcreateddate')
        form = EventForm()
        events_count = len(events)
        currentTime = timezone.now()
        context = {
            'events': events,
            'events_count': events_count,
            'currentTime': currentTime,
        }
        return render(request, 'social/allevents.html', context)

class CreatedEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(eventcreater=request.user).filter(isDeleted=False).order_by('-eventcreateddate')
        number_of_createdevent = len(events)
        form = EventForm()
        currentTime = timezone.now()
        context = {
            'events': events,
            'number_of_createdevent': number_of_createdevent,
            'currentTime': currentTime,
        }
        return render(request, 'social/createdevents.html', context)

class AppliedEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(isDeleted=False)
        eventapplications = EventApplication.objects.all()
        eventsapplied = []
        for eventapplication in eventapplications:
            for event in events:
                if eventapplication.event == event:
                    if eventapplication.applicant == request.user:
                        eventsapplied.append(event)
        number_of_appliedevent = len(eventsapplied)
        form = EventForm()
        currentTime = timezone.now()
        context = {
            'events': events,
            'eventapplied': eventsapplied,
            'number_of_appliedevent': number_of_appliedevent,
            'currentTime': currentTime,
        }
        return render(request, 'social/appliedevents.html', context)

class EventApplicationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = EventApplication
    template_name = 'social/event-application_delete.html'

    def get_success_url(self):
        event_pk = self.kwargs['event_pk']
        event = Event.objects.get(pk=event_pk)
        application = self.get_object()
        applicant_user_profile = UserProfile.objects.get(pk=application.applicant.pk)
        notification = NotifyUser.objects.create(notify=event.eventcreater, notification=str(applicant_user_profile.user.username)+' canceled application for event '+str(event.eventname), offerType="event", offerPk=event.pk)
        notified_user = UserProfile.objects.get(pk=event.eventcreater)
        notified_user.unreadcount = notified_user.unreadcount+1
        notified_user.save()
        log = Log.objects.create(operation="deleteeventapplication", itemType="event", itemId=event.pk, affectedItemType="user", affectedItemId=application.applicant.pk, userId=self.request.user)
        applicationsNext = EventApplication.objects.filter(event=event).filter(approved=False).order_by('-date')
        count = 0
        for applicationNext in applicationsNext:
            if count == 0:
                applicationNext.approved = True
                applicationNext.save()
                count = 1
        return reverse_lazy('event-detail', kwargs={'pk': event_pk})
    
    def test_func(self):
        application = self.get_object()
        isOK = False
        if self.request.user == application.applicant:
            isOK = True
        if self.request.user == application.event.eventcreater:
            isOK = True
        return isOK

class EventDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        notifications = NotifyUser.objects.filter(notify=request.user).filter(offerType="event").filter(offerPk=pk).filter(hasRead=False)
        countNotifications = len(notifications)
        for notification in notifications:
            notification.hasRead = True
            notification.save()
        userNotified = UserProfile.objects.get(pk=request.user.profile)
        userNotified.unreadcount = userNotified.unreadcount - countNotifications
        userNotified.save()
        applications = EventApplication.objects.filter(event=pk).order_by('-date')
        applications_this = applications.filter(applicant=request.user)
        number_of_accepted = len(applications.filter(approved=True))
        accepted_applications = applications.filter(approved=True)
        application_number = len(applications)
        is_active = True
        if event.eventdate <= timezone.now():
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
            'event': event,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_applied': is_applied,
            'applications_this': applications_this,
            'is_accepted': is_accepted,
            'is_active': is_active,
            'application_number': application_number,
            'accepted_applications': accepted_applications
        }
        return render(request, 'social/event_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        form = EventApplicationForm(request.POST)
        applications = EventApplication.objects.filter(event=pk).order_by('-date')
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
                new_application.event = event
                if number_of_accepted < event.eventcapacity:
                    new_application.approved = True
                else:
                    new_application.approved = False
                new_application.save()
                log = Log.objects.create(operation="createeventapplication", itemType="event", itemId=event.pk, userId=request.user)
                notification = NotifyUser.objects.create(notify=event.eventcreater, notification=str(new_application.applicant)+' applied to event '+str(new_application.event.eventname), offerType="event", offerPk=new_application.event.pk)
                notified_user = UserProfile.objects.get(pk=event.eventcreater)
                notified_user.unreadcount = notified_user.unreadcount+1
                notified_user.save()
        context = {
            'event': event,
            'form': form,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_applied': is_applied,
            'applications_this': applications_this,
        }
        return redirect('event-detail', pk=event.pk)

class EventEditView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        event = Event.objects.get(pk=pk)
        if event.eventcreater == request.user:
            if event.eventdate > timezone.now():
                form = EventForm(instance = event)
                context = {
                    'form': form,
                }
                return render(request, 'social/event_edit.html', context)
            else:
                return redirect('event-detail', pk=event.pk)
        else:
            return redirect('event-detail', pk=event.pk)

    def post(self, request, *args, pk, **kwargs):
        form = EventForm(request.POST, request.FILES)
        event = Event.objects.get(pk=pk)
        applications = EventApplication.objects.filter(event=event)
        number_of_accepted = len(applications.filter(approved=True))
        if form.is_valid():
            edit_event = form.save(commit=False)
            if edit_event.eventcapacity < number_of_accepted:
                messages.warning(request, 'You cannot make the capacity below the accepted number.')
            else:
                event.eventpicture = event.eventpicture
                if request.FILES:
                    event.eventpicture = edit_event.eventpicture
                event.eventname = edit_event.eventname
                event.eventdescription = edit_event.eventdescription
                event.eventdate = edit_event.eventdate
                event.eventlocation = edit_event.eventlocation
                event.eventcapacity = edit_event.eventcapacity
                event.eventduration = edit_event.eventduration
                event.save()
                log = Log.objects.create(operation="editevent", itemType="event", itemId=event.pk, userId=request.user)
                messages.success(request, 'Event editing is successful.')
                for application in applications:
                    notification = NotifyUser.objects.create(notify=application.applicant, notification=str(event.eventname)+' event which you applied is edited.', offerType="event", offerPk=event.pk)
                    notified_user = UserProfile.objects.get(pk=application.applicant)
                    notified_user.unreadcount = notified_user.unreadcount+1
                    notified_user.save()
        context = {
            'form': form,
        }
        return render(request, 'social/event_edit.html', context)

class EventDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        event = Event.objects.get(pk=pk)
        if event.eventcreater == request.user:
            if event.eventdate > timezone.now():
                form = EventForm(instance = event)
                context = {
                    'form': form,
                }
                return render(request, 'social/event_delete.html', context)
            else:
                return redirect('event-detail', pk=event.pk)
        else:
            return redirect('event-detail', pk=event.pk)

    def post(self, request, *args, pk, **kwargs):
        event = Event.objects.get(pk=pk)
        applications = EventApplication.objects.filter(event=event)
        for application in applications:
            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(event.eventname)+' event which you applied is deleted.', offerType="event")
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount+1
            notified_user.save()
            notificationsToChange = NotifyUser.objects.filter(notify=application.applicant).filter(hasRead=False).filter(offerType="event").filter(offerPk=pk)
            log1 = Log.objects.create(operation="deleteeventapplication", itemType="event", itemId=event.pk, affectedItemType="user", affectedItemId=application.applicant.pk, userId=request.user)
            application.delete()
            for notificationChange in notificationsToChange:
                notificationChange.offerPk = 0
                notificationChange.save()
        log2 = Log.objects.create(operation="deleteevent", itemType="event", itemId=event.pk, userId=request.user)
        event.isDeleted = True
        event.save()
        return redirect('allevents')

class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        followers = profile.followers.all()
        ratings_average = UserRatings.objects.filter(rated=profile.user).aggregate(Avg('rating'))
        if len(followers) == 0:
            is_following = False
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False
        number_of_followers = len(followers)
        services = Service.objects.filter(creater=profile.user).filter(isDeleted=False)
        number_of_services = len(services)
        events = Event.objects.filter(eventcreater=profile.user).filter(isDeleted=False)
        number_of_events = len(events)
        comments = UserRatings.objects.filter(rated=profile.user)
        context = {
            'user': user,
            'profile': profile,
            'number_of_followers': number_of_followers,
            'is_following': is_following,
            'ratings_average': ratings_average,
            'comments': comments,
            'services': services,
            'number_of_services': number_of_services,
            'events': events,
            'number_of_events': number_of_events,
        }
        return render(request, 'social/profile.html', context)

class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        if profile.user == request.user:
            form = ProfileForm(instance = profile)
            context = {
                'form': form,
            }
            return render(request, 'social/profile_edit.html', context)
        else:
            return redirect('profile', pk=profile.pk)

    def post(self, request, *args, pk, **kwargs):
        form = ProfileForm(request.POST, request.FILES)
        profile = UserProfile.objects.get(pk=pk)
        if form.is_valid():
            edit_profile = form.save(commit=False)
            profile.picture = profile.picture
            if request.FILES:
                profile.picture = edit_profile.picture
            profile.name = edit_profile.name
            profile.bio = edit_profile.bio
            profile.birth_date = edit_profile.birth_date
            profile.location = edit_profile.location
            profile.save()
            log = Log.objects.create(operation="editprofile", itemType="user", itemId=pk, userId=request.user)
            messages.success(request, 'Profile editing is successful.')
        context = {
            'form': form,
        }
        return render(request, 'social/profile_edit.html', context)

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        follow_pk = self.kwargs['followpk']
        profile = UserProfile.objects.get(pk=follow_pk)
        profile.followers.add(request.user)
        log = Log.objects.create(operation="follow", itemType="user", itemId=follow_pk, userId=request.user)
        return redirect('profile', pk=follow_pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        follow_pk = self.kwargs['followpk']
        profile = UserProfile.objects.get(pk=follow_pk)
        profile.followers.remove(request.user)
        log = Log.objects.create(operation="unfollow", itemType="user", itemId=follow_pk, userId=request.user)
        return redirect('profile', pk=follow_pk)

class RemoveMyFollower(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower_pk = self.kwargs['follower_pk']
        follower = UserProfile.objects.get(pk=follower_pk).user
        profile = UserProfile.objects.get(pk=request.user.pk)
        profile.followers.remove(follower)
        log = Log.objects.create(operation="removemyfollower", itemType="user", itemId=follower_pk, userId=request.user)
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

class RateUser(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = RatingForm()
        servicepk = self.kwargs['servicepk']
        service = Service.objects.get(pk=servicepk)
        ratedpk = self.kwargs['ratedpk']
        rated = UserProfile.objects.get(user=ratedpk)
        ratingRecord = UserRatings.objects.filter(service=service).filter(rated=rated.user).filter(rater=request.user)
        isRated = len(ratingRecord)
        context = {
            'form': form,
            'ratingRecord': ratingRecord,
            'isRated': isRated,
            'service': service,
            'rated': rated,
        }
        return render(request, 'social/rating.html', context)
    
    def post(self, request, *args, **kwargs):
        form = RatingForm(request.POST)
        servicepk = self.kwargs['servicepk']
        service = Service.objects.get(pk=servicepk)
        ratedpk = self.kwargs['ratedpk']
        rated = UserProfile.objects.get(user=ratedpk)
        if form.is_valid():
            new_rating = form.save(commit=False)
            new_rating.rater = request.user
            new_rating.service = service
            new_rating.rated = rated.user
            new_rating.save()
            log = Log.objects.create(operation="createrating", itemType="service", itemId=service.pk, affectedItemType="user", affectedItemId=new_rating.rated.pk, userId=request.user)
            messages.success(request, 'Rating is successful.')
        return redirect('service-detail', pk=servicepk)

class RateUserEdit(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        rating = UserRatings.objects.get(pk=pk)
        form = RatingForm(instance = rating)     
        context = {
            'form': form,
            'rating': rating,
        }
        return render(request, 'social/rating-edit.html', context)

    def post(self, request, *args, pk, **kwargs):
        form = RatingForm(request.POST)
        rating = UserRatings.objects.get(pk=pk)
        if form.is_valid():
            edit_rating = form.save(commit=False)
            rating.rating = edit_rating.rating
            rating.feedback = edit_rating.feedback
            rating.save()     
            log = Log.objects.create(operation="editrating", itemType="service", itemId=rating.service.pk, affectedItemType="user", affectedItemId=rating.rated.pk, userId=request.user) 
            messages.success(request, 'Rating editing is successful.')
        context = {
            'form': form,
        }
        return render(request, 'social/rating-edit.html', context)

class RateUserDelete(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        rating = UserRatings.objects.get(pk=pk)
        form = RatingForm(instance = rating)
        context = {
            'form': form,
        }
        return render(request, 'social/rating-delete.html', context)

    def post(self, request, *args, pk, **kwargs):
        rating = UserRatings.objects.get(pk=pk)
        service = rating.service
        log = Log.objects.create(operation="deleterating", itemType="service", itemId=rating.service.pk, affectedItemType="user", affectedItemId=rating.rated.pk, userId=request.user)
        rating.delete()
        return redirect('service-detail', pk=service.pk)

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
        services = Service.objects.filter(isDeleted=False).order_by('-createddate')
        events = Event.objects.filter(isDeleted=False).order_by('-eventcreateddate')
        for one in followedOnes:
            for service in services:
                if service.creater == one.user :
                    services2.append(service)
            for event in events:
                if event.eventcreater == one.user :
                    events2.append(event)
        events_count = len(events2)
        services_count = len(services2)
        currentTime = timezone.now()
        context = {
            'services': services2,
            'events': events2,
            'services_count': services_count,
            'events_count': events_count,
            'currentTime': currentTime,
        }
        return render(request, 'social/timeline.html', context)

class ServiceSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        services = Service.objects.filter(isDeleted=False).filter(Q(name__icontains=query))
        services_count = len(services)
        currentTime = timezone.now()
        alltags = Tag.objects.all()
        context = {
            'services': services,
            'services_count': services_count,
            'currentTime': currentTime,
            'alltags': alltags,
        }
        return render(request, 'social/service-search.html', context)

class EventSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        events = Event.objects.filter(isDeleted=False).filter(Q(eventname__icontains=query))
        events_count = len(events)
        currentTime = timezone.now()
        context = {
            'events': events,
            'events_count': events_count,
            'currentTime': currentTime,
        }
        return render(request, 'social/event-search.html', context)

class Notifications(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        notifications = NotifyUser.objects.filter(notify=request.user).filter(hasRead=False)
        notifications_count = len(notifications)
        notificationsToRead = notifications.filter(offerPk=0)
        countNotifications = len(notificationsToRead)
        for notification in notificationsToRead:
            notification.hasRead = True
            notification.save()
        userNotified = UserProfile.objects.get(pk=request.user.profile)
        userNotified.unreadcount = userNotified.unreadcount - countNotifications
        userNotified.save()
        context = {
            'notifications': notifications,
            'notifications_count': notifications_count,
        }
        return render(request, 'social/notifications.html', context)
    
class RequestCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = RequestForm()
        context = {
            'form': form,
        }
        return render(request, 'social/request_create.html', context)
    
    def post(self, request, *args, **kwargs):
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.requester = request.user
            new_request.save()
            messages.success(request, 'Request creation is successful.')
            if(new_request.toPerson):
                notification = NotifyUser.objects.create(notify=new_request.toPerson, notification=str(new_request.requester.username)+' requested service tag '+str(new_request.tag), offerType="request", offerPk=new_request.pk)
                notified_user = UserProfile.objects.get(pk=new_request.toPerson)
                notified_user.unreadcount = notified_user.unreadcount+1
                notified_user.save()
        context = {
            'form': form,
        }
        return render(request, 'social/request_create.html', context)

class CreatedRequestsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        requests = Tag.objects.filter(requester=request.user)
        number_of_requests = len(requests)
        context = {
            'requests': requests,
            'number_of_requests': number_of_requests,
        }
        return render(request, 'social/createdrequests.html', context)

class RequestsFromMeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        requests = Tag.objects.filter(toPerson=request.user)
        number_of_requests = len(requests)
        context = {
            'requests': requests,
            'number_of_requests': number_of_requests,
        }
        return render(request, 'social/requestsfromme.html', context)

class RequestDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        requestDetail = Tag.objects.get(pk=pk)
        notifications = NotifyUser.objects.filter(notify=request.user).filter(offerType="request").filter(offerPk=pk).filter(hasRead=False)
        countNotifications = len(notifications)
        for notification in notifications:
            notification.hasRead = True
            notification.save()
        userNotified = UserProfile.objects.get(pk=request.user.profile)
        userNotified.unreadcount = userNotified.unreadcount - countNotifications
        userNotified.save()
        context = {
            'requestDetail': requestDetail,
        }
        return render(request, 'social/request_detail.html', context)

class RequestDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        requestToDelete = Tag.objects.get(pk=pk)
        if requestToDelete.requester == request.user:
            form = RequestForm(instance = requestToDelete)
            context = {
                'form': form,
            }
            return render(request, 'social/request_delete.html', context)
        else:
            return redirect('request-detail', pk=requestToDelete.pk)

    def post(self, request, *args, pk, **kwargs):
        requestToDelete = Tag.objects.get(pk=pk)
        notification = NotifyUser.objects.create(notify=requestToDelete.toPerson, notification=str(requestToDelete.tag)+' request from you is deleted.', offerType="request")
        notified_user = UserProfile.objects.get(pk=requestToDelete.toPerson)
        notified_user.unreadcount = notified_user.unreadcount+1
        notified_user.save()
        notificationsToChange = NotifyUser.objects.filter(notify=requestToDelete.toPerson).filter(hasRead=False).filter(offerType="request").filter(offerPk=pk)
        for notificationChange in notificationsToChange:
            notificationChange.offerPk = 0
            notificationChange.save() 
        servicesToEdit = Service.objects.filter(category=requestToDelete.pk)
        for serviceToEdit in servicesToEdit:
            serviceToEdit.category = None
        requestToDelete.delete()
        return redirect('createdrequests')

class ServiceFilter(View):
    def get(self, request, *args, **kwargs):
        category = self.request.GET.get('category')
        if category != "all":
            services = Service.objects.filter(category=category).filter(isDeleted=False)
        else:
            services = Service.objects.filter(isDeleted=False).order_by('-createddate')
        services_count = len(services)
        currentTime = timezone.now()
        alltags = Tag.objects.all()
        context = {
            'services': services,
            'services_count': services_count,
            'currentTime': currentTime,
            'alltags': alltags,
        }
        return render(request, 'social/service-filter.html', context)

class AllUsersView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        users = UserProfile.objects.all()
        context = {
            'users': users,
        }
        return render(request, 'social/allusers.html', context)

class UsersServicesListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        services = Service.objects.filter(creater=profile.user).filter(isDeleted=False)
        number_of_services = len(services)
        context = {
            'services': services,
            'profile': profile,
            'number_of_services': number_of_services
        }
        return render(request, 'social/usersservices.html', context)

class UsersEventsListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        events = Event.objects.filter(eventcreater=profile.user).filter(isDeleted=False)
        number_of_events = len(events)
        context = {
            'events': events,
            'profile': profile,
            'number_of_events': number_of_events
        }
        return render(request, 'social/usersevents.html', context)

class AddAdminView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.isAdmin = True
        profile.save()
        log = Log.objects.create(operation="addadmin", itemType="user", itemId=pk, userId=request.user)
        return redirect('profile', pk=pk)

class RemoveAdminView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.isAdmin = False
        profile.save()
        log = Log.objects.create(operation="removeadmin", itemType="user", itemId=pk, userId=request.user)
        return redirect('profile', pk=pk)

class DashboardEventDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        applications = EventApplication.objects.filter(event=pk).order_by('-date')
        number_of_accepted = len(applications.filter(approved=True))
        application_number = len(applications)
        is_active = True
        if event.eventcreateddate <= timezone.now():
            is_active = False
        logs = Log.objects.filter(itemType="event").filter(itemId=pk)
        conversion = {'createevent': 'Event Creation',
                      'createeventapplication': 'Event Application Creation',
                      'editevent': 'Event Edition',
                      'deleteevent': 'Event Deletion',
                      'editserviceapplication': 'Service Application Edition',
                      'deleteeventapplication': 'Event Application Deletion',
                      'spentcredit': 'Credit Spent',
                      'createeventcommunication': 'Message Sent'}
        for log in logs:
            log.operation = conversion[log.operation]
        context = {
            'event': event,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_active': is_active,
            'application_number': application_number,
            'logs': logs,
            'isDeleted': event.isDeleted
        }
        return render(request, 'social/dashboard_event_detail.html', context)

class DashboardServiceDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        applications = ServiceApplication.objects.filter(service=pk).order_by('-date')
        number_of_accepted = len(applications.filter(approved=True))
        application_number = len(applications)
        is_active = True
        if service.servicedate <= timezone.now():
            is_active = False
        logs = Log.objects.filter(itemType="service").filter(itemId=pk)
        conversion = {'createservice': 'Service Creation',
                      'createserviceapplication': 'Service Application Creation',
                      'editservice': 'Service Edition',
                      'deleteservice': 'Service Deletion',
                      'editserviceapplication': 'Service Application Edition',
                      'deleteserviceapplication': 'Service Application Deletion',
                      'confirmtaken': 'Confirmation of Service Taken',
                      'confirmgiven': 'Confirmation of Service Given',
                      'earncredit': 'Credit Earned',
                      'spentcredit': 'Credit Spent',
                      'createservicecommunication': 'Message Sent',
                      'createrating': 'Rating Created',
                      'editrating': 'Rating Edited',
                      'deleterating': 'Rating Deleted'}
        for log in logs:
            log.operation = conversion[log.operation]

        context = {
            'service': service,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_active': is_active,
            'application_number': application_number,
            'logs': logs
        }
        return render(request, 'social/dashboard_service_detail.html', context)

class ServiceDetailCommunicationView(View):
    def get(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        query = self.request.GET.get('query')
        if(query == ""):
            messages.warning(request, 'Please write something to post.')
        else:
            communication = Communication.objects.create(itemType="service", itemId=service.pk, communicated=request.user, message=query)
            notification = NotifyUser.objects.create(notify=service.creater, notification=str(request.user)+' commented on '+str(service.name), offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=service.creater)
            notified_user.unreadcount = notified_user.unreadcount+1
            notified_user.save()
            log = Log.objects.create(operation="createservicecommunication", itemType="service", itemId=service.pk, userId=request.user)
        notifications = NotifyUser.objects.filter(notify=request.user).filter(offerType="service").filter(offerPk=pk).filter(hasRead=False)
        countNotifications = len(notifications)
        for notification in notifications:
            notification.hasRead = True
            notification.save()
        userNotified = UserProfile.objects.get(pk=request.user.profile)
        userNotified.unreadcount = userNotified.unreadcount - countNotifications
        userNotified.save()
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
        allCommunications = Communication.objects.filter(itemType="service").filter(itemId=service.pk)
        allCommunicationsLength = len(allCommunications)
        context = {
            'service': service,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_applied': is_applied,
            'applications_this': applications_this,
            'is_accepted': is_accepted,
            'is_active': is_active,
            'application_number': application_number,
            'accepted_applications': accepted_applications,
            'allCommunications': allCommunications,
            'allCommunicationsLength': allCommunicationsLength
        }
        return render(request, 'social/service_detail_communication.html', context)

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
                oldApplications = ServiceApplication.objects.filter(applicant=request.user).filter(approved=False)
                for oldApplication in oldApplications:
                    if oldApplication.service.servicedate <= timezone.now() and oldApplication.service.is_given == False and oldApplication.service.is_taken == False:
                        applicant_user_profile.reservehour = applicant_user_profile.reservehour + oldApplication.service.duration
                        oldApplication.service.is_given = True
                        oldApplication.service.is_taken = True
                        oldApplication.save()
                oldServices = Service.objects.filter(creater=request.user).filter(is_given=False).filter(is_taken=False).filter(isDeleted=False)
                applicationsForOldServiceCheck = ServiceApplication.objects.all()
                for oldService in oldServices:
                    if oldService.servicedate <= timezone.now():
                        if len(applicationsForOldServiceCheck.filter(service=oldService)) == 0 or len(applicationsForOldServiceCheck.filter(service=oldService).filter(approved=True)) == 0:
                            applicant_user_profile.reservehour = applicant_user_profile.reservehour - oldService.duration
                            oldService.is_taken = True
                            oldService.is_given = True
                            oldService.save()
                totalcredit = applicant_user_profile.reservehour + applicant_user_profile.credithour
                if totalcredit >= service.duration:
                    new_application = form.save(commit=False)
                    new_application.applicant = request.user
                    new_application.service = service
                    new_application.approved = False
                    new_application.save()
                    log = Log.objects.create(operation="createserviceapplication", itemType="service", itemId=service.pk, userId=request.user)
                    applicant_user_profile.reservehour = applicant_user_profile.reservehour - service.duration
                    applicant_user_profile.save()
                    notification = NotifyUser.objects.create(notify=service.creater, notification=str(new_application.applicant)+' applied to service '+str(new_application.service.name), offerType="service", offerPk=new_application.service.pk)
                    notified_user = UserProfile.objects.get(pk=service.creater)
                    notified_user.unreadcount = notified_user.unreadcount+1
                    notified_user.save()
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
        return redirect('service-detail-communication', pk=service.pk)
