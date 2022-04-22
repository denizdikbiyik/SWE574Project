from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Service, UserProfile, Event, ServiceApplication, UserRatings, NotifyUser, EventApplication, Tag, \
    Log, Communication, Like, UserComplaints, Featured
from .forms import ServiceForm, EventForm, ServiceApplicationForm, RatingForm, EventApplicationForm, ProfileForm, \
    RequestForm, ComplaintForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Q
from datetime import timedelta
from online_users.models import OnlineUserActivity

# MatPlotLib
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np


class ServiceCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        request.session["type"] = "service"
        form = ServiceForm()
        context = {
            'form': form,
        }
        return render(request, 'social/service_create.html', context)

    def post(self, request, *args, **kwargs):
        services = Service.objects.filter(isDeleted=False).filter(isActive=True).order_by('-createddate')
        creater_user_profile = UserProfile.objects.get(pk=request.user)
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            totalcredit = creater_user_profile.reservehour + creater_user_profile.credithour
            new_service = form.save(commit=False)
            if totalcredit + new_service.duration <= 15:
                sameDateServices = Service.objects.filter(creater=request.user).filter(
                    servicedate=new_service.servicedate).filter(isDeleted=False).filter(isActive=True)
                sameDateEvents = Event.objects.filter(eventcreater=request.user).filter(
                    eventdate=new_service.servicedate).filter(isDeleted=False).filter(isActive=True)
                if len(sameDateServices) > 0 or len(sameDateEvents) > 0:
                    messages.warning(request,
                                     'You cannot create this service because you have one with the same datetime.')
                else:
                    new_service.creater = request.user
                    creater_user_profile.reservehour = creater_user_profile.reservehour + new_service.duration
                    creater_user_profile.save()
                    if new_service.category:
                        notification = NotifyUser.objects.create(notify=new_service.category.requester,
                                                                 notification=str(
                                                                     request.user) + ' created service with your request ' + str(
                                                                     new_service.category) + '.', offerType="request",
                                                                 offerPk=0)
                        notified_user = UserProfile.objects.get(pk=new_service.category.requester)
                        notified_user.unreadcount = notified_user.unreadcount + 1
                        notified_user.save()
                    new_service.wiki_description = request.session['description']  # Added by AT
                    request.session['description'] = None  # Added by AT
                    new_service.save()
                    messages.success(request, 'Service creation is successful.')
                    request.session["type"] = None
                    log = Log.objects.create(operation="createservice", itemType="service", itemId=new_service.pk,
                                             userId=request.user)
            else:
                messages.warning(request, 'You cannot create this service which causes credit hours exceed 15.')
        context = {
            'service_list': services,
            'form': form,
        }
        return render(request, 'social/service_create.html', context)


class AllServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        currentTime = timezone.now()
        services = Service.objects.all().order_by('-createddate').filter(isDeleted=False).filter(isActive=True).filter(
            servicedate__gte=currentTime)
        alltags = Tag.objects.all()
        form = ServiceForm()
        services_count = len(services)
        context = {
            'services': services,
            'services_count': services_count,
            'currentTime': currentTime,
            'alltags': alltags,
        }
        return render(request, 'social/allservices.html', context)


class CreatedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.filter(creater=request.user).filter(isDeleted=False).filter(isActive=True).order_by(
            '-createddate')
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
        serviceapplications = ServiceApplication.objects.filter(isDeleted=False).filter(isActive=True)
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
        is_featured = False
        featured = Featured.objects.filter(itemId=pk).filter(itemType="service")
        if len(featured) > 0:
            is_featured = True
        showCommunication = False
        if request.user == service.creater or request.user.profile.isAdmin == True:
            showCommunication = True
        notifications = NotifyUser.objects.filter(notify=request.user).filter(offerType="service").filter(
            offerPk=pk).filter(hasRead=False)
        countNotifications = len(notifications)
        for notification in notifications:
            notification.hasRead = True
            notification.save()
        userNotified = UserProfile.objects.get(pk=request.user.profile)
        userNotified.unreadcount = userNotified.unreadcount - countNotifications
        userNotified.save()
        applications = ServiceApplication.objects.filter(service=pk).filter(isDeleted=False).filter(
            isActive=True).order_by('-date')
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
                if is_accepted:
                    showCommunication = True
                break
            else:
                is_applied = False
                is_accepted = False
        allCommunications = Communication.objects.filter(itemType="service").filter(itemId=service.pk)
        allCommunicationsLength = len(allCommunications)
        is_like = Like.objects.filter(itemType="service").filter(itemId=pk).filter(liked=request.user)
        likes = Like.objects.filter(itemType="service").filter(itemId=pk)
        likesCount = len(likes)
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
            'allCommunicationsLength': allCommunicationsLength,
            'showCommunication': showCommunication,
            'is_like': is_like,
            'likes': likes,
            'likesCount': likesCount,
            'is_featured': is_featured
        }
        return render(request, 'social/service_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        form = ServiceApplicationForm(request.POST)
        applications = ServiceApplication.objects.filter(service=pk).filter(isDeleted=False).filter(
            isActive=True).order_by('-date')
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
                oldApplications = ServiceApplication.objects.filter(applicant=request.user).filter(
                    approved=False).filter(isDeleted=False).filter(isActive=True)
                for oldApplication in oldApplications:
                    if oldApplication.service.servicedate <= timezone.now() and oldApplication.service.is_given == False and oldApplication.service.is_taken == False:
                        applicant_user_profile.reservehour = applicant_user_profile.reservehour + oldApplication.service.duration
                        oldApplication.service.is_given = True
                        oldApplication.service.is_taken = True
                        oldApplication.save()
                oldServices = Service.objects.filter(creater=request.user).filter(is_given=False).filter(
                    is_taken=False).filter(isDeleted=False).filter(isActive=True)
                applicationsForOldServiceCheck = ServiceApplication.objects.filter(isDeleted=False).filter(
                    isActive=True)
                for oldService in oldServices:
                    if oldService.servicedate <= timezone.now():
                        if len(applicationsForOldServiceCheck.filter(service=oldService)) == 0 or len(
                                applicationsForOldServiceCheck.filter(service=oldService).filter(approved=True)) == 0:
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
                    log = Log.objects.create(operation="createserviceapplication", itemType="service",
                                             itemId=service.pk, userId=request.user)
                    applicant_user_profile.reservehour = applicant_user_profile.reservehour - service.duration
                    applicant_user_profile.save()
                    notification = NotifyUser.objects.create(notify=service.creater, notification=str(
                        new_application.applicant) + ' applied to service ' + str(new_application.service.name),
                                                             offerType="service", offerPk=new_application.service.pk)
                    notified_user = UserProfile.objects.get(pk=service.creater)
                    notified_user.unreadcount = notified_user.unreadcount + 1
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


class ApplicationDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        application = ServiceApplication.objects.get(pk=pk)
        if request.user == application.applicant or request.user == application.service.creater:
            if application.service.servicedate > timezone.now():
                form = ServiceApplicationForm(instance=application)
                context = {
                    'form': form,
                }
                return render(request, 'social/application_delete.html', context)
            else:
                return redirect('service-detail', pk=application.service.pk)
        else:
            return redirect('service-detail', pk=application.service.pk)

    def post(self, request, *args, pk, **kwargs):
        service_pk = self.kwargs['service_pk']
        service = Service.objects.get(pk=service_pk)
        application = ServiceApplication.objects.get(pk=pk)
        applicant_user_profile = UserProfile.objects.get(pk=application.applicant.pk)
        service_creater_profile = UserProfile.objects.get(pk=service.creater.pk)
        applicant_user_profile.reservehour = applicant_user_profile.reservehour + service.duration
        applicant_user_profile.save()
        if request.user == application.applicant:
            notification = NotifyUser.objects.create(notify=service.creater, notification=str(
                applicant_user_profile.user.username) + ' canceled application for service ' + str(service.name),
                                                     offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=service.creater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            application.deletionInfo = "cancel"
        elif request.user == application.service.creater:
            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                service_creater_profile.user.username) + ' rejected your application for service ' + str(service.name),
                                                     offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            application.deletionInfo = "reject"
        log = Log.objects.create(operation="deleteserviceapplication", itemType="service", itemId=service.pk,
                                 affectedItemType="user", affectedItemId=application.applicant.pk,
                                 userId=self.request.user)
        application.isDeleted = True
        application.save()
        return redirect('service-detail', pk=application.service.pk)


class ApplicationEditView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        application = ServiceApplication.objects.get(pk=pk)
        if application.service.creater == request.user:
            form = ServiceApplicationForm(instance=application)
            context = {
                'form': form,
            }
            return render(request, 'social/application_edit.html', context)
        else:
            return redirect('service-detail', pk=application.service.pk)

    def post(self, request, *args, pk, **kwargs):
        form = ServiceApplicationForm(request.POST, request.FILES)
        application = ServiceApplication.objects.get(pk=pk)
        if form.is_valid():
            edit_application = form.save(commit=False)
            application.approved = edit_application.approved
            application.save()
            notification = NotifyUser.objects.create(notify=application.applicant,
                                                     notification='Your application status for ' + str(
                                                         application.service.name) + ' is changed by the owner.',
                                                     offerType="service", offerPk=application.service.pk)
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            log = Log.objects.create(operation="editserviceapplication", itemType="service",
                                     itemId=application.service.pk, affectedItemType="user",
                                     affectedItemId=application.applicant.pk, userId=self.request.user)
        context = {
            'form': form,
        }
        return redirect('service-detail', pk=application.service.pk)


class ConfirmServiceTaken(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        service.is_taken = True
        service.save()
        CreditExchange(service)
        applications = ServiceApplication.objects.filter(service=pk).filter(approved=True).filter(
            isDeleted=False).filter(isActive=True)
        for application in applications:
            notification = NotifyUser.objects.create(notify=application.applicant,
                                                     notification=str(service.name) + ' taken confirmation done.',
                                                     offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
        notification = NotifyUser.objects.create(notify=service.creater,
                                                 notification=str(service.name) + ' taken confirmation done.',
                                                 offerType="service", offerPk=service.pk)
        notified_user = UserProfile.objects.get(pk=service.creater)
        notified_user.unreadcount = notified_user.unreadcount + 1
        notified_user.save()
        log = Log.objects.create(operation="confirmtaken", itemType="service", itemId=service.pk, userId=request.user)
        return redirect('service-detail', pk=pk)


class ConfirmServiceGiven(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        service.is_given = True
        service.save()
        CreditExchange(service)
        applications = ServiceApplication.objects.filter(service=pk).filter(approved=True).filter(
            isDeleted=False).filter(isActive=True)
        for application in applications:
            notification = NotifyUser.objects.create(notify=application.applicant,
                                                     notification=str(service.name) + ' given confirmation done.',
                                                     offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
        log = Log.objects.create(operation="confirmgiven", itemType="service", itemId=service.pk, userId=request.user)
        return redirect('service-detail', pk=pk)


def CreditExchange(service):
    applications = ServiceApplication.objects.filter(service=service.pk).filter(approved=True).filter(
        isDeleted=False).filter(isActive=True)
    notConfirmedApplications = ServiceApplication.objects.filter(service=service.pk).filter(approved=False).filter(
        isDeleted=False).filter(isActive=True)
    if service.is_taken == True:
        if service.is_given == True:
            service_giver = UserProfile.objects.get(pk=service.creater.pk)
            service_giver.credithour = service_giver.credithour + service.duration
            service_giver.reservehour = service_giver.reservehour - service.duration
            service_giver.save()
            log1 = Log.objects.create(operation="earncredit", itemType="service", itemId=service.pk,
                                      affectedItemType="user", affectedItemId=service.creater.pk,
                                      userId=service.creater)
            for application in applications:
                service_taker = UserProfile.objects.get(pk=application.applicant.pk)
                service_taker.credithour = service_taker.credithour - service.duration
                service_taker.reservehour = service_taker.reservehour + service.duration
                service_taker.save()
                log2 = Log.objects.create(operation="spentcredit", itemType="service", itemId=service.pk,
                                          affectedItemType="user", affectedItemId=application.applicant.pk,
                                          userId=application.applicant)
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
                form = ServiceForm(instance=service)
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
            applications = ServiceApplication.objects.filter(service=service).filter(isDeleted=False).filter(
                isActive=True)
            totalcredit = service_creater_profile.reservehour + service_creater_profile.credithour - service.duration
            edit_service = form.save(commit=False)
            if totalcredit + edit_service.duration <= 15:
                applications = ServiceApplication.objects.filter(service=service).filter(isDeleted=False).filter(
                    isActive=True)
                number_of_accepted = len(applications.filter(approved=True))
                if edit_service.capacity < number_of_accepted:
                    messages.warning(request,
                                     'You cannot make capacity below the accepted number, please remove accepted participants.')
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
                    log = Log.objects.create(operation="editservice", itemType="service", itemId=service.pk,
                                             userId=request.user)
                    messages.success(request, 'Service editing is successful.')
                    applications = ServiceApplication.objects.filter(service=service).filter(isDeleted=False).filter(
                        isActive=True)
                    for application in applications:
                        notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                            service.name) + ' which you applied is edited.', offerType="service", offerPk=service.pk)
                        notified_user = UserProfile.objects.get(pk=application.applicant)
                        notified_user.unreadcount = notified_user.unreadcount + 1
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
                form = ServiceForm(instance=service)
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
        applications = ServiceApplication.objects.filter(service=service).filter(isDeleted=False).filter(isActive=True)
        for application in applications:
            service_applicant_profile = UserProfile.objects.get(pk=application.applicant)
            service_applicant_profile.reservehour = service_applicant_profile.reservehour + service.duration
            service_applicant_profile.save()
            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                service.name) + ' service which you applied is deleted.', offerType="service")
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            notificationsToChange = NotifyUser.objects.filter(notify=application.applicant).filter(
                hasRead=False).filter(offerType="service").filter(offerPk=pk)
            for notificationChange in notificationsToChange:
                notificationChange.offerPk = 0
                notificationChange.save()
            log1 = Log.objects.create(operation="deleteserviceapplication", itemType="service", itemId=service.pk,
                                      affectedItemType="user", affectedItemId=application.applicant.pk,
                                      userId=request.user)
            application.deletionInfo = "serviceDeleted"
            application.isDeleted = True
            application.save()
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
        request.session["type"] = "event"
        form = EventForm()
        context = {
            'form': form,
        }
        return render(request, 'social/event_create.html', context)

    def post(self, request, *args, **kwargs):
        events = Event.objects.filter(isDeleted=False).filter(isActive=True).order_by('-eventcreateddate')
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            new_event = form.save(commit=False)
            sameDateEvents = Event.objects.filter(eventcreater=request.user).filter(
                eventdate=new_event.eventdate).filter(isDeleted=False).filter(isActive=True)
            sameDateServices = Service.objects.filter(creater=request.user).filter(
                servicedate=new_event.eventdate).filter(isDeleted=False).filter(isActive=True)
            if len(sameDateEvents) > 0 or len(sameDateServices) > 0:
                messages.warning(request, 'You cannot create this event because you have one with the same datetime.')
            else:
                new_event.eventcreater = request.user
                new_event.event_wiki_description = request.session['description']  # Added by AT
                request.session['description'] = None  # Added by AT
                new_event.save()
                log = Log.objects.create(operation="createevent", itemType="event", itemId=new_event.pk,
                                         userId=request.user)
                messages.success(request, 'Event creation is successful.')
                request.session["type"] = None
        context = {
            'event_list': events,
            'form': form,
        }
        return render(request, 'social/event_create.html', context)


class AllEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        currentTime = timezone.now()
        events = Event.objects.filter(isDeleted=False).filter(isActive=True).filter(
            eventdate__gte=currentTime).order_by('-eventcreateddate')
        form = EventForm()
        events_count = len(events)
        context = {
            'events': events,
            'events_count': events_count,
            'currentTime': currentTime,
        }
        return render(request, 'social/allevents.html', context)


class CreatedEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(eventcreater=request.user).filter(isDeleted=False).filter(isActive=True).order_by(
            '-eventcreateddate')
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
        eventapplications = EventApplication.objects.filter(isDeleted=False).filter(isActive=True)
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


class EventApplicationDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        application = EventApplication.objects.get(pk=pk)
        if request.user == application.applicant or request.user == application.event.eventcreater:
            if application.event.eventdate > timezone.now():
                form = EventApplicationForm(instance=application)
                context = {
                    'form': form,
                }
                return render(request, 'social/event-application_delete.html', context)
            else:
                return redirect('event-detail', pk=application.event.pk)
        else:
            return redirect('event-detail', pk=application.event.pk)

    def post(self, request, *args, pk, **kwargs):
        event_pk = self.kwargs['event_pk']
        event = Event.objects.get(pk=event_pk)
        application = EventApplication.objects.get(pk=pk)
        applicant_user_profile = UserProfile.objects.get(pk=application.applicant.pk)
        event_creater_profile = UserProfile.objects.get(pk=event.eventcreater.pk)
        if request.user == application.applicant:
            notification = NotifyUser.objects.create(notify=event.eventcreater, notification=str(
                applicant_user_profile.user.username) + ' canceled application for event ' + str(event.eventname),
                                                     offerType="event", offerPk=event.pk)
            notified_user = UserProfile.objects.get(pk=event.eventcreater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            application.deletionInfo = "cancel"
        elif request.user == application.event.eventcreater:
            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                event_creater_profile.user.username) + ' rejected your application for event ' + str(event.eventname),
                                                     offerType="event", offerPk=event.pk)
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            application.deletionInfo = "reject"
        log = Log.objects.create(operation="deleteeventapplication", itemType="event", itemId=event.pk,
                                 affectedItemType="user", affectedItemId=application.applicant.pk,
                                 userId=self.request.user)
        applicationsNext = EventApplication.objects.filter(event=event).filter(approved=False).filter(
            isDeleted=False).filter(isActive=True).order_by('-date')
        count = 0
        for applicationNext in applicationsNext:
            if count == 0:
                applicationNext.approved = True
                applicationNext.save()
                count = 1
        application.isDeleted = True
        application.save()
        return redirect('event-detail', pk=application.event.pk)


class EventDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        is_featured = False
        featured = Featured.objects.filter(itemId=pk).filter(itemType="event")
        if len(featured) > 0:
            is_featured = True
        showCommunication = False
        if request.user == event.eventcreater or request.user.profile.isAdmin == True:
            showCommunication = True
        notifications = NotifyUser.objects.filter(notify=request.user).filter(offerType="event").filter(
            offerPk=pk).filter(hasRead=False)
        countNotifications = len(notifications)
        for notification in notifications:
            notification.hasRead = True
            notification.save()
        userNotified = UserProfile.objects.get(pk=request.user.profile)
        userNotified.unreadcount = userNotified.unreadcount - countNotifications
        userNotified.save()
        applications = EventApplication.objects.filter(event=pk).filter(isDeleted=False).filter(isActive=True).order_by(
            '-date')
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
                if is_accepted:
                    showCommunication = True
                break
            else:
                is_applied = False
                is_accepted = False
        allCommunications = Communication.objects.filter(itemType="event").filter(itemId=event.pk)
        allCommunicationsLength = len(allCommunications)
        is_like = Like.objects.filter(itemType="event").filter(itemId=pk).filter(liked=request.user)
        likes = Like.objects.filter(itemType="event").filter(itemId=pk)
        likesCount = len(likes)
        context = {
            'event': event,
            'applications': applications,
            'number_of_accepted': number_of_accepted,
            'is_applied': is_applied,
            'applications_this': applications_this,
            'is_accepted': is_accepted,
            'is_active': is_active,
            'application_number': application_number,
            'accepted_applications': accepted_applications,
            'allCommunications': allCommunications,
            'allCommunicationsLength': allCommunicationsLength,
            'showCommunication': showCommunication,
            'is_like': is_like,
            'likes': likes,
            'likesCount': likesCount,
            'is_featured': is_featured
        }
        return render(request, 'social/event_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        form = EventApplicationForm(request.POST)
        applications = EventApplication.objects.filter(event=pk).filter(isDeleted=False).filter(isActive=True).order_by(
            '-date')
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
                log = Log.objects.create(operation="createeventapplication", itemType="event", itemId=event.pk,
                                         userId=request.user)
                notification = NotifyUser.objects.create(notify=event.eventcreater, notification=str(
                    new_application.applicant) + ' applied to event ' + str(new_application.event.eventname),
                                                         offerType="event", offerPk=new_application.event.pk)
                notified_user = UserProfile.objects.get(pk=event.eventcreater)
                notified_user.unreadcount = notified_user.unreadcount + 1
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
                form = EventForm(instance=event)
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
        applications = EventApplication.objects.filter(event=event).filter(isDeleted=False).filter(isActive=True)
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
                    notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                        event.eventname) + ' event which you applied is edited.', offerType="event", offerPk=event.pk)
                    notified_user = UserProfile.objects.get(pk=application.applicant)
                    notified_user.unreadcount = notified_user.unreadcount + 1
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
                form = EventForm(instance=event)
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
        applications = EventApplication.objects.filter(event=event).filter(isDeleted=False).filter(isActive=True)
        for application in applications:
            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                event.eventname) + ' event which you applied is deleted.', offerType="event")
            notified_user = UserProfile.objects.get(pk=application.applicant)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            notificationsToChange = NotifyUser.objects.filter(notify=application.applicant).filter(
                hasRead=False).filter(offerType="event").filter(offerPk=pk)
            log1 = Log.objects.create(operation="deleteeventapplication", itemType="event", itemId=event.pk,
                                      affectedItemType="user", affectedItemId=application.applicant.pk,
                                      userId=request.user)
            application.deletionInfo = "eventDeleted"
            application.isDeleted = True
            application.save()
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
        services = Service.objects.filter(creater=profile.user).filter(isDeleted=False).filter(isActive=True)
        number_of_services = len(services)
        events = Event.objects.filter(eventcreater=profile.user).filter(isDeleted=False).filter(isActive=True)
        number_of_events = len(events)
        comments = UserRatings.objects.filter(rated=profile.user)

        followings = []
        allUsers = UserProfile.objects.all()
        for userTo in allUsers:
            userFollowers = userTo.followers.all()
            for userFollower in userFollowers:
                if profile.user.pk == userFollower.pk:
                    followings.append(userTo)
        number_of_followings = len(followings)

        notifications = NotifyUser.objects.filter(notify=request.user).filter(offerType="user").filter(
            offerPk=pk).filter(hasRead=False)
        countNotifications = len(notifications)
        for notification in notifications:
            notification.hasRead = True
            notification.save()
        userNotified = UserProfile.objects.get(pk=request.user.profile)
        userNotified.unreadcount = userNotified.unreadcount - countNotifications
        userNotified.save()

        context = {
            'user': user,
            'profile': profile,
            'number_of_followers': number_of_followers,
            'number_of_followings': number_of_followings,
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
            form = ProfileForm(instance=profile)
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
        return redirect('followings', pk=request.user.pk)


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


class FollowingsListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followings = []
        allUsers = UserProfile.objects.all()
        for userTo in allUsers:
            userFollowers = userTo.followers.all()
            for userFollower in userFollowers:
                if profile.user.pk == userFollower.pk:
                    followings.append(userTo)
        number_of_followings = len(followings)
        context = {
            'followings': followings,
            'profile': profile,
            'number_of_followings': number_of_followings
        }
        return render(request, 'social/followings_list.html', context)


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
            log = Log.objects.create(operation="createrating", itemType="service", itemId=service.pk,
                                     affectedItemType="user", affectedItemId=new_rating.rated.pk, userId=request.user)
            messages.success(request, 'Rating is successful.')
        return redirect('service-detail', pk=servicepk)


class RateUserEdit(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        rating = UserRatings.objects.get(pk=pk)
        form = RatingForm(instance=rating)
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
            log = Log.objects.create(operation="editrating", itemType="service", itemId=rating.service.pk,
                                     affectedItemType="user", affectedItemId=rating.rated.pk, userId=request.user)
            messages.success(request, 'Rating editing is successful.')
        context = {
            'form': form,
        }
        return render(request, 'social/rating-edit.html', context)


class RateUserDelete(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        rating = UserRatings.objects.get(pk=pk)
        form = RatingForm(instance=rating)
        context = {
            'form': form,
        }
        return render(request, 'social/rating-delete.html', context)

    def post(self, request, *args, pk, **kwargs):
        rating = UserRatings.objects.get(pk=pk)
        service = rating.service
        log = Log.objects.create(operation="deleterating", itemType="service", itemId=rating.service.pk,
                                 affectedItemType="user", affectedItemId=rating.rated.pk, userId=request.user)
        rating.delete()
        return redirect('service-detail', pk=service.pk)


class TimeLine(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        currentTime = timezone.now()
        profile = UserProfile.objects.get(pk=request.user.pk)
        allUsers = UserProfile.objects.all()
        followedOnes = []
        services2 = []
        events2 = []
        for auser in allUsers:
            thisFollowers = UserProfile.objects.get(pk=auser.pk).followers.all()
            if request.user in thisFollowers:
                followedOnes.append(auser)
        services = Service.objects.filter(isDeleted=False).filter(isActive=True).filter(
            servicedate__gte=currentTime).order_by('-createddate')
        events = Event.objects.filter(isDeleted=False).filter(isActive=True).filter(
            eventdate__gte=currentTime).order_by('-eventcreateddate')
        for one in followedOnes:
            for service in services:
                if service.creater == one.user:
                    services2.append(service)
            for event in events:
                if event.eventcreater == one.user:
                    events2.append(event)
        events_count = len(events2)
        services_count = len(services2)
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
        currentTime = timezone.now()
        services = Service.objects.filter(isDeleted=False).filter(isActive=True).filter(
            servicedate__gte=currentTime).filter(Q(name__icontains=query))
        services_count = len(services)
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
        currentTime = timezone.now()
        events = Event.objects.filter(isDeleted=False).filter(isActive=True).filter(eventdate__gte=currentTime).filter(
            Q(eventname__icontains=query))
        events_count = len(events)
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
            if (new_request.toPerson):
                notification = NotifyUser.objects.create(notify=new_request.toPerson, notification=str(
                    new_request.requester.username) + ' requested service tag ' + str(new_request.tag),
                                                         offerType="request", offerPk=new_request.pk)
                notified_user = UserProfile.objects.get(pk=new_request.toPerson)
                notified_user.unreadcount = notified_user.unreadcount + 1
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
        notifications = NotifyUser.objects.filter(notify=request.user).filter(offerType="request").filter(
            offerPk=pk).filter(hasRead=False)
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
            form = RequestForm(instance=requestToDelete)
            context = {
                'form': form,
            }
            return render(request, 'social/request_delete.html', context)
        else:
            return redirect('request-detail', pk=requestToDelete.pk)

    def post(self, request, *args, pk, **kwargs):
        requestToDelete = Tag.objects.get(pk=pk)
        notification = NotifyUser.objects.create(notify=requestToDelete.toPerson, notification=str(
            requestToDelete.tag) + ' request from you is deleted.', offerType="request")
        notified_user = UserProfile.objects.get(pk=requestToDelete.toPerson)
        notified_user.unreadcount = notified_user.unreadcount + 1
        notified_user.save()
        notificationsToChange = NotifyUser.objects.filter(notify=requestToDelete.toPerson).filter(hasRead=False).filter(
            offerType="request").filter(offerPk=pk)
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
        currentTime = timezone.now()
        if category != "all":
            services = Service.objects.filter(category=category).filter(isDeleted=False).filter(isActive=True).filter(
                servicedate__gte=currentTime)
        else:
            services = Service.objects.filter(isDeleted=False).filter(isActive=True).filter(
                servicedate__gte=currentTime).order_by('-createddate')
        services_count = len(services)
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
        users = UserProfile.objects.filter(isActive=True)
        context = {
            'users': users,
        }
        return render(request, 'social/allusers.html', context)


class UsersServicesListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        services = Service.objects.filter(creater=profile.user).filter(isDeleted=False).filter(isActive=True)
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
        events = Event.objects.filter(eventcreater=profile.user).filter(isDeleted=False).filter(isActive=True)
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
        if event.eventdate <= timezone.now():
            is_active = False
        logs = Log.objects.filter(itemType="event").filter(itemId=pk)
        conversion = {'createevent': 'Event is created.',
                      'createeventapplication': 'Application done to event.',
                      'editevent': 'Event is edited.',
                      'deleteevent': 'Event is deleted.',
                      'editserviceapplication': 'Service application is edited.',
                      'deleteeventapplication': 'Event application is deleted.',
                      'spentcredit': 'Credit spent.',
                      'createeventcommunication': 'A message sent under event.',
                      'deleteeventcommunication': 'A message under event is deleted.',
                      'like': 'Event is liked.',
                      'unlike': 'Event is unliked.',
                      'deactivate': 'Event is deactivated.',
                      'deactivateeventapplication': 'An application to event is deactivated.'}
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
        conversion = {'createservice': 'Service is created.',
                      'createserviceapplication': 'Application done to service.',
                      'editservice': 'Service is edited.',
                      'deleteservice': 'Service is deleted.',
                      'editserviceapplication': 'An application to service is edited.',
                      'deleteserviceapplication': 'An application to service is deleted.',
                      'confirmtaken': 'Service taken is confirmed.',
                      'confirmgiven': 'Service given is confirmed.',
                      'earncredit': 'Credit earned.',
                      'spentcredit': 'Credit spent.',
                      'createservicecommunication': 'A message sent under service.',
                      'deleteservicecommunication': 'A message under service is deleted.',
                      'createrating': 'A rating is created.',
                      'editrating': 'A rating is edited.',
                      'deleterating': 'A rating is deleted.',
                      'like': 'Service is liked.',
                      'unlike': 'Service is unliked.',
                      'deactivate': 'Service is deactivated.',
                      'deactivateserviceapplication': 'An application to service is deactivated.'}
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
        if (query == ""):
            messages.warning(request, 'Please write something to post.')
        else:
            communication = Communication.objects.create(itemType="service", itemId=service.pk,
                                                         communicated=request.user, message=query)
            if request.user != service.creater:
                notification = NotifyUser.objects.create(notify=service.creater,
                                                         notification=str(request.user) + ' commented on ' + str(
                                                             service.name), offerType="service", offerPk=service.pk)
                notified_user = UserProfile.objects.get(pk=service.creater)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
            log = Log.objects.create(operation="createservicecommunication", itemType="service", itemId=service.pk,
                                     userId=request.user)
        applications = ServiceApplication.objects.filter(service=pk).filter(isDeleted=False).filter(
            isActive=True).order_by('-date')
        for applicationToNotify in applications:
            if applicationToNotify.applicant != request.user:
                notification = NotifyUser.objects.create(notify=applicationToNotify.applicant,
                                                         notification=str(request.user) + ' commented on ' + str(
                                                             service.name), offerType="service", offerPk=service.pk)
                notified_user = UserProfile.objects.get(pk=applicationToNotify.applicant)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
        return redirect('service-detail', pk=service.pk)


class ServiceCommunicationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Communication
    template_name = 'social/service_communication_delete.html'

    def get_success_url(self):
        service_pk = self.kwargs['service_pk']
        service = Service.objects.get(pk=service_pk)
        communication = self.get_object()
        if self.request.user != service.creater:
            notification = NotifyUser.objects.create(notify=service.creater, notification=str(
                self.request.user) + ' deleted communication message on service ' + str(service.name),
                                                     offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=service.creater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
        approvedApplications = ServiceApplication.objects.filter(approved=True).filter(isDeleted=False).filter(
            isActive=True)
        for approvedApplication in approvedApplications:
            if self.request.user != approvedApplication.applicant:
                notification = NotifyUser.objects.create(notify=approvedApplication.applicant, notification=str(
                    self.request.user) + ' deleted communication message on service ' + str(service.name),
                                                         offerType="service", offerPk=service.pk)
                notified_user = UserProfile.objects.get(pk=approvedApplication.applicant)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
        log = Log.objects.create(operation="deleteservicecommunication", itemType="service", itemId=service.pk,
                                 userId=self.request.user)
        return reverse_lazy('service-detail', kwargs={'pk': service_pk})

    def test_func(self):
        communication = self.get_object()
        isOK = False
        if self.request.user == communication.communicated:
            isOK = True
        if self.request.user.profile.isAdmin:
            isOK = True
        return isOK


class EventDetailCommunicationView(View):
    def get(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        query = self.request.GET.get('query')
        if (query == ""):
            messages.warning(request, 'Please write something to post.')
        else:
            communication = Communication.objects.create(itemType="event", itemId=event.pk, communicated=request.user,
                                                         message=query)
            if request.user != event.eventcreater:
                notification = NotifyUser.objects.create(notify=event.eventcreater,
                                                         notification=str(request.user) + ' commented on ' + str(
                                                             event.eventname), offerType="event", offerPk=event.pk)
                notified_user = UserProfile.objects.get(pk=event.eventcreater)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
            log = Log.objects.create(operation="createeventcommunication", itemType="event", itemId=event.pk,
                                     userId=request.user)
        applications = EventApplication.objects.filter(event=pk).filter(isDeleted=False).filter(isActive=True).order_by(
            '-date')
        for applicationToNotify in applications:
            if applicationToNotify.applicant != request.user:
                notification = NotifyUser.objects.create(notify=applicationToNotify.applicant,
                                                         notification=str(request.user) + ' commented on ' + str(
                                                             event.eventname), offerType="event", offerPk=event.pk)
                notified_user = UserProfile.objects.get(pk=applicationToNotify.applicant)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
        return redirect('event-detail', pk=event.pk)


class EventCommunicationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Communication
    template_name = 'social/event_communication_delete.html'

    def get_success_url(self):
        event_pk = self.kwargs['event_pk']
        event = Event.objects.get(pk=event_pk)
        communication = self.get_object()
        if self.request.user != event.eventcreater:
            notification = NotifyUser.objects.create(notify=event.eventcreater, notification=str(
                self.request.user) + ' deleted communication message on event ' + str(event.eventname),
                                                     offerType="event", offerPk=event.pk)
            notified_user = UserProfile.objects.get(pk=event.eventcreater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
        approvedApplications = EventApplication.objects.filter(approved=True).filter(isDeleted=False).filter(
            isActive=True)
        for approvedApplication in approvedApplications:
            if self.request.user != approvedApplication.applicant:
                notification = NotifyUser.objects.create(notify=approvedApplication.applicant, notification=str(
                    self.request.user) + ' deleted communication message on event ' + str(event.eventname),
                                                         offerType="event", offerPk=event.pk)
                notified_user = UserProfile.objects.get(pk=approvedApplication.applicant)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
        log = Log.objects.create(operation="deleteeventcommunication", itemType="event", itemId=event.pk,
                                 userId=self.request.user)
        return reverse_lazy('event-detail', kwargs={'pk': event_pk})

    def test_func(self):
        communication = self.get_object()
        isOK = False
        if self.request.user == communication.communicated:
            isOK = True
        if self.request.user.profile.isAdmin:
            isOK = True
        return isOK


class ServiceLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        like = Like.objects.create(itemType="service", itemId=pk, liked=request.user)
        notification = NotifyUser.objects.create(notify=service.creater,
                                                 notification=str(request.user) + ' liked service ' + str(service.name),
                                                 offerType="service", offerPk=service.pk)
        notified_user = UserProfile.objects.get(pk=service.creater)
        notified_user.unreadcount = notified_user.unreadcount + 1
        notified_user.save()
        log = Log.objects.create(operation="like", itemType="service", itemId=pk, userId=request.user)
        return redirect('service-detail', pk=pk)


class ServiceUnlike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        like = Like.objects.get(itemType="service", itemId=pk, liked=request.user)
        like.delete()
        notification = NotifyUser.objects.create(notify=service.creater,
                                                 notification=str(request.user) + ' unliked service ' + str(
                                                     service.name), offerType="service", offerPk=service.pk)
        notified_user = UserProfile.objects.get(pk=service.creater)
        notified_user.unreadcount = notified_user.unreadcount + 1
        notified_user.save()
        log = Log.objects.create(operation="unlike", itemType="service", itemId=pk, userId=request.user)
        return redirect('service-detail', pk=pk)


class EventLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        like = Like.objects.create(itemType="event", itemId=pk, liked=request.user)
        notification = NotifyUser.objects.create(notify=event.eventcreater,
                                                 notification=str(request.user) + ' liked event ' + str(
                                                     event.eventname), offerType="event", offerPk=event.pk)
        notified_user = UserProfile.objects.get(pk=event.eventcreater)
        notified_user.unreadcount = notified_user.unreadcount + 1
        notified_user.save()
        log = Log.objects.create(operation="like", itemType="event", itemId=pk, userId=request.user)
        return redirect('event-detail', pk=pk)


class EventUnlike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        like = Like.objects.get(itemType="event", itemId=pk, liked=request.user)
        like.delete()
        notification = NotifyUser.objects.create(notify=event.eventcreater,
                                                 notification=str(request.user) + ' unliked event ' + str(
                                                     event.eventname), offerType="event", offerPk=event.pk)
        notified_user = UserProfile.objects.get(pk=event.eventcreater)
        notified_user.unreadcount = notified_user.unreadcount + 1
        notified_user.save()
        log = Log.objects.create(operation="unlike", itemType="event", itemId=pk, userId=request.user)
        return redirect('event-detail', pk=pk)


class ServiceLikesList(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        likes = Like.objects.filter(itemType="service").filter(itemId=pk)
        likesCount = len(likes)
        context = {
            'likes': likes,
            'likesCount': likesCount,
            'service': service
        }
        return render(request, 'social/service_like_list.html', context)


class EventLikesList(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        likes = Like.objects.filter(itemType="event").filter(itemId=pk)
        likesCount = len(likes)
        context = {
            'likes': likes,
            'likesCount': likesCount,
            'event': event
        }
        return render(request, 'social/event_like_list.html', context)


class MyLikes(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        likes = Like.objects.filter(liked=request.user)
        service_likes = likes.filter(itemType="service")
        event_likes = likes.filter(itemType="event")
        services = []
        for service_like in service_likes:
            serviceToAdd = Service.objects.get(pk=service_like.itemId)
            services.append(serviceToAdd)
        events = []
        for event_like in event_likes:
            eventToAdd = Event.objects.get(pk=event_like.itemId)
            events.append(eventToAdd)
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
        return render(request, 'social/mylikes.html', context)


class AdminDashboardIndex(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # user_activity_objects_15min = OnlineUserActivity.get_user_activities()
        # number_of_active_users_15min = user_activity_objects_15min.count()

        # user_activity_objects_60min = OnlineUserActivity.get_user_activities(timedelta(minutes=60))
        # users_60min = (user for user in user_activity_objects_60min)

        user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(seconds=5))
        number_of_active_users = user_activity_objects.count()
        activeUsers = (user for user in user_activity_objects)

        allUsers = UserProfile.objects.all()
        allUsersCount = len(allUsers) - number_of_active_users

        labels = []
        data = []

        labels.append("Not Active Users")
        labels.append("Active Users")

        data.append(allUsersCount)
        data.append(number_of_active_users)

        explode = (0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
        fig1, ax1 = plt.subplots()
        # ax1.pie(data, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.pie(data, explode=explode, labels=labels, autopct=lambda p: '{:.0f}'.format(p * sum(data) / 100),
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.savefig('media/users_chart.png', dpi=100)

        context = {
            'activeUsers': activeUsers,
            'number_of_active_users': number_of_active_users,
            'allUsers': allUsers,
            'allUsersCount': allUsersCount,
        }
        return render(request, 'social/admindashboardindex.html', context)


class OnlineUsersList(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(seconds=5))
        number_of_active_users = user_activity_objects.count()
        activeUsers = (user for user in user_activity_objects)
        users = []
        for user in activeUsers:
            profile = UserProfile.objects.get(pk=user.pk)
            users.append(profile)

        context = {
            'activeUsers': activeUsers,
            'number_of_active_users': number_of_active_users,
            'users': users,
        }
        return render(request, 'social/onlineusers.html', context)


class ComplaintUser(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        form = ComplaintForm()
        complainted = UserProfile.objects.get(user=pk)
        complaintRecord = UserComplaints.objects.filter(complainted=complainted.user).filter(
            complainter=request.user).filter(isDeleted=False)
        isComplainted = len(complaintRecord)
        context = {
            'form': form,
            'complaintRecord': complaintRecord,
            'isComplainted': isComplainted,
            'complainted': complainted,
        }
        return render(request, 'social/complaint.html', context)

    def post(self, request, *args, pk, **kwargs):
        form = ComplaintForm(request.POST)
        complainted = UserProfile.objects.get(user=pk)
        if form.is_valid():
            new_complaint = form.save(commit=False)
            new_complaint.complainter = request.user
            new_complaint.complainted = complainted.user
            new_complaint.save()
            log = Log.objects.create(operation="createcomplaint", itemType="user", itemId=complainted.pk,
                                     userId=request.user)
            allAdmins = UserProfile.objects.filter(isAdmin=True)
            for admin in allAdmins:
                notification = NotifyUser.objects.create(notify=admin.user,
                                                         notification=str(request.user) + ' complainted for ' + str(
                                                             complainted.user), offerType="user",
                                                         offerPk=complainted.user.pk)
                notified_user = UserProfile.objects.get(pk=admin.user)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
            messages.success(request, 'Complaint is successful.')
        return redirect('profile', pk=pk)


class ComplaintUserEdit(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        complaint = UserComplaints.objects.get(pk=pk)
        form = ComplaintForm(instance=complaint)
        context = {
            'form': form,
            'complaint': complaint,
        }
        return render(request, 'social/complaint-edit.html', context)

    def post(self, request, *args, pk, **kwargs):
        form = ComplaintForm(request.POST)
        complaint = UserComplaints.objects.get(pk=pk)
        if form.is_valid():
            edit_complaint = form.save(commit=False)
            complaint.feedback = edit_complaint.feedback
            complaint.save()
            log = Log.objects.create(operation="editcomplaint", itemType="user", itemId=complaint.complainted.pk,
                                     userId=request.user)
            allAdmins = UserProfile.objects.filter(isAdmin=True)
            for admin in allAdmins:
                notification = NotifyUser.objects.create(notify=admin.user, notification=str(
                    request.user) + ' edited complaint for ' + str(complaint.complainted), offerType="user",
                                                         offerPk=complaint.complainted.pk)
                notified_user = UserProfile.objects.get(pk=admin.user)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
        context = {
            'form': form,
        }
        return redirect('complaintuser', pk=complaint.complainted.pk)


class ComplaintUserDelete(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        complaint = UserComplaints.objects.get(pk=pk)
        form = ComplaintForm(instance=complaint)
        context = {
            'form': form,
        }
        return render(request, 'social/complaint-delete.html', context)

    def post(self, request, *args, pk, **kwargs):
        complaint = UserComplaints.objects.get(pk=pk)
        complaint.isDeleted = True
        complaint.save()
        log = Log.objects.create(operation="deletecomplaint", itemType="user", itemId=complaint.complainted.pk,
                                 userId=request.user)
        allAdmins = UserProfile.objects.filter(isAdmin=True)
        for admin in allAdmins:
            notification = NotifyUser.objects.create(notify=admin.user,
                                                     notification=str(request.user) + ' deleted complaint for ' + str(
                                                         complaint.complainted), offerType="user",
                                                     offerPk=complaint.complainted.pk)
            notified_user = UserProfile.objects.get(pk=admin.user)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
        return redirect('profile', pk=complaint.complainted.pk)


class Complaints(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        complaints = UserComplaints.objects.all()
        complaints_count = len(complaints)
        context = {
            'complaints_count': complaints_count,
            'complaints': complaints,
        }
        return render(request, 'social/complaints.html', context)


class MyComplaints(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        complaints = UserComplaints.objects.filter(complainter=request.user).filter(isDeleted=False)
        complaints_count = len(complaints)
        context = {
            'complaints_count': complaints_count,
            'complaints': complaints,
        }
        return render(request, 'social/mycomplaints.html', context)


class DeactivateService(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        service = Service.objects.get(pk=pk)
        service.isActive = False
        service.save()
        notificationsToChange = NotifyUser.objects.filter(hasRead=False).filter(offerType="service").filter(offerPk=pk)
        for notificationChange in notificationsToChange:
            notificationChange.offerPk = 0
            notificationChange.save()
        service.creater.profile.reservehour = service.creater.profile.reservehour - service.duration
        notification = NotifyUser.objects.create(notify=service.creater,
                                                 notification=str(request.user) + ' deactivated your service ' + str(
                                                     service.name), offerType="service", offerPk=0)
        service.creater.profile.unreadcount = service.creater.profile.unreadcount + 1
        service.creater.profile.save()
        serviceApplications = ServiceApplication.objects.filter(service=service).filter(isDeleted=False).filter(
            isActive=True)
        for serviceApplication in serviceApplications:
            serviceApplication.isActive = False
            serviceApplication.save()
            serviceApplication.applicant.profile.reservehour = serviceApplication.applicant.profile.reservehour + service.duration
            notification = NotifyUser.objects.create(notify=serviceApplication.applicant,
                                                     notification=str(request.user) + ' deactivated the service ' + str(
                                                         service.name) + ' that you applied.', offerType="service",
                                                     offerPk=0)
            serviceApplication.applicant.profile.unreadcount = serviceApplication.applicant.profile.unreadcount + 1
            serviceApplication.applicant.profile.save()
        log = Log.objects.create(operation="deactivate", itemType="service", itemId=pk, userId=request.user)
        return redirect('service-detail', pk=pk)


class DeactivateEvent(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        event = Event.objects.get(pk=pk)
        event.isActive = False
        event.save()
        notificationsToChange = NotifyUser.objects.filter(hasRead=False).filter(offerType="event").filter(offerPk=pk)
        for notificationChange in notificationsToChange:
            notificationChange.offerPk = 0
            notificationChange.save()
        notification = NotifyUser.objects.create(notify=event.eventcreater,
                                                 notification=str(request.user) + ' deactivated your event ' + str(
                                                     event.eventname), offerType="event", offerPk=0)
        event.eventcreater.profile.unreadcount = event.eventcreater.profile.unreadcount + 1
        event.eventcreater.profile.save()
        eventApplications = EventApplication.objects.filter(event=event).filter(isDeleted=False).filter(isActive=True)
        for eventApplication in eventApplications:
            eventApplication.isActive = False
            eventApplication.save()
            notification = NotifyUser.objects.create(notify=eventApplication.applicant,
                                                     notification=str(request.user) + ' deactivated the event ' + str(
                                                         event.eventname) + ' that you applied.', offerType="event",
                                                     offerPk=0)
            eventApplication.applicant.profile.unreadcount = eventApplication.applicant.profile.unreadcount + 1
            eventApplication.applicant.profile.save()
        log = Log.objects.create(operation="deactivate", itemType="event", itemId=pk, userId=request.user)
        return redirect('event-detail', pk=pk)


class DeactivateUser(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.isActive = False
        profile.save()

        notification = NotifyUser.objects.create(notify=profile.user,
                                                 notification=str(request.user) + ' deactivated your profile.',
                                                 offerType="user", offerPk=0)
        profile.unreadcount = profile.unreadcount + 1
        profile.save()

        profileServices = Service.objects.filter(creater=profile.user).filter(isActive=True).filter(isDeleted=False)
        for service in profileServices:
            if service.servicedate > timezone.now():
                service.isActive = False
                service.save()
                notificationsToChange = NotifyUser.objects.filter(hasRead=False).filter(offerType="service").filter(
                    offerPk=service.pk)
                for notificationChange in notificationsToChange:
                    notificationChange.offerPk = 0
                    notificationChange.save()
                service.creater.profile.reservehour = service.creater.profile.reservehour - service.duration
                notification = NotifyUser.objects.create(notify=service.creater, notification=str(
                    request.user) + ' deactivated your service ' + str(service.name), offerType="service", offerPk=0)
                service.creater.profile.unreadcount = service.creater.profile.unreadcount + 1
                service.creater.profile.save()
                serviceApplications = ServiceApplication.objects.filter(service=service).filter(isDeleted=False).filter(
                    isActive=True)
                for serviceApplication in serviceApplications:
                    serviceApplication.isActive = False
                    serviceApplication.save()
                    serviceApplication.applicant.profile.reservehour = serviceApplication.applicant.profile.reservehour + service.duration
                    notification = NotifyUser.objects.create(notify=serviceApplication.applicant, notification=str(
                        request.user) + ' deactivated the service ' + str(service.name) + ' that you applied.',
                                                             offerType="service", offerPk=0)
                    serviceApplication.applicant.profile.unreadcount = serviceApplication.applicant.profile.unreadcount + 1
                    serviceApplication.applicant.profile.save()
                log = Log.objects.create(operation="deactivate", itemType="service", itemId=service.pk,
                                         userId=request.user)

        profileEvents = Event.objects.filter(eventcreater=profile.user).filter(isActive=True).filter(isDeleted=False)
        for event in profileEvents:
            if event.eventdate > timezone.now():
                event.isActive = False
                event.save()
                notificationsToChange = NotifyUser.objects.filter(hasRead=False).filter(offerType="event").filter(
                    offerPk=event.pk)
                for notificationChange in notificationsToChange:
                    notificationChange.offerPk = 0
                    notificationChange.save()
                notification = NotifyUser.objects.create(notify=event.eventcreater, notification=str(
                    request.user) + ' deactivated your event ' + str(event.eventname), offerType="event", offerPk=0)
                event.eventcreater.profile.unreadcount = event.eventcreater.profile.unreadcount + 1
                event.eventcreater.profile.save()
                eventApplications = EventApplication.objects.filter(event=event).filter(isDeleted=False).filter(
                    isActive=True)
                for eventApplication in eventApplications:
                    eventApplication.isActive = False
                    eventApplication.save()
                    notification = NotifyUser.objects.create(notify=eventApplication.applicant, notification=str(
                        request.user) + ' deactivated the event ' + str(event.eventname) + ' that you applied.',
                                                             offerType="event", offerPk=0)
                    eventApplication.applicant.profile.unreadcount = eventApplication.applicant.profile.unreadcount + 1
                    eventApplication.applicant.profile.save()
                log = Log.objects.create(operation="deactivate", itemType="event", itemId=event.pk, userId=request.user)

        profileServiceApplications = ServiceApplication.objects.filter(applicant=profile.user).filter(
            isActive=True).filter(isDeleted=False)
        for theserviceApplication in profileServiceApplications:
            if theserviceApplication.service.servicedate > timezone.now():
                theserviceApplication.isActive = False
                theserviceApplication.save()
                theserviceApplication.applicant.profile.reservehour = theserviceApplication.applicant.profile.reservehour + theserviceApplication.service.duration
                notification = NotifyUser.objects.create(notify=theserviceApplication.applicant, notification=str(
                    request.user) + ' deactivated your application for service ' + str(
                    theserviceApplication.service.name) + '.', offerType="service", offerPk=0)
                theserviceApplication.applicant.profile.unreadcount = theserviceApplication.applicant.profile.unreadcount + 1
                theserviceApplication.applicant.profile.save()
                notification = NotifyUser.objects.create(notify=theserviceApplication.service.creater, notification=str(
                    request.user) + ' deactivated the application of ' + str(
                    theserviceApplication.applicant) + ' for your service ' + str(
                    theserviceApplication.service.name) + '.', offerType="service", offerPk=0)
                theserviceApplication.service.creater.profile.unreadcount = theserviceApplication.service.creater.profile.unreadcount + 1
                theserviceApplication.service.creater.profile.save()

        profileEventApplications = EventApplication.objects.filter(applicant=profile.user).filter(isActive=True).filter(
            isDeleted=False)
        for theeventApplication in profileEventApplications:
            if theeventApplication.event.eventdate > timezone.now():
                theeventApplication.isActive = False
                theeventApplication.save()
                notification = NotifyUser.objects.create(notify=theeventApplication.applicant, notification=str(
                    request.user) + ' deactivated your application for event ' + str(
                    theeventApplication.event.eventname) + '.', offerType="event", offerPk=0)
                theeventApplication.applicant.profile.unreadcount = theeventApplication.applicant.profile.unreadcount + 1
                theeventApplication.applicant.profile.save()
                notification = NotifyUser.objects.create(notify=theeventApplication.event.eventcreater,
                                                         notification=str(
                                                             request.user) + ' deactivated the application of ' + str(
                                                             theeventApplication.applicant) + ' for your event ' + str(
                                                             theeventApplication.event.eventname) + '.',
                                                         offerType="event", offerPk=0)
                theeventApplication.event.eventcreater.profile.unreadcount = theeventApplication.event.eventcreater.profile.unreadcount + 1
                theeventApplication.event.eventcreater.profile.save()
                applicationsNext = EventApplication.objects.filter(event=theeventApplication.event).filter(
                    approved=False).filter(isDeleted=False).filter(isActive=True).order_by('-date')
                count = 0
                for applicationNext in applicationsNext:
                    if count == 0:
                        applicationNext.approved = True
                        applicationNext.save()
                        count = 1

        log = Log.objects.create(operation="deactivate", itemType="user", itemId=pk, userId=request.user)
        return redirect('profile', pk=pk)


class ActivateUser(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.isActive = True
        profile.save()
        log = Log.objects.create(operation="activate", itemType="user", itemId=pk, userId=request.user)
        return redirect('profile', pk=pk)


class DeactivateServiceApplication(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        theserviceApplication = ServiceApplication.objects.get(pk=pk)
        theserviceApplication.isActive = False
        theserviceApplication.save()
        theserviceApplication.applicant.profile.reservehour = theserviceApplication.applicant.profile.reservehour + theserviceApplication.service.duration
        notification = NotifyUser.objects.create(notify=theserviceApplication.applicant, notification=str(
            request.user) + ' deactivated your application for service ' + str(
            theserviceApplication.service.name) + '.', offerType="service", offerPk=theserviceApplication.service.pk)
        theserviceApplication.applicant.profile.unreadcount = theserviceApplication.applicant.profile.unreadcount + 1
        theserviceApplication.applicant.profile.save()
        notification = NotifyUser.objects.create(notify=theserviceApplication.service.creater, notification=str(
            request.user) + ' deactivated the application of ' + str(
            theserviceApplication.applicant) + ' for your service ' + str(theserviceApplication.service.name) + '.',
                                                 offerType="service", offerPk=theserviceApplication.service.pk)
        theserviceApplication.service.creater.profile.unreadcount = theserviceApplication.service.creater.profile.unreadcount + 1
        theserviceApplication.service.creater.profile.save()
        log = Log.objects.create(operation="deactivateserviceapplication", itemType="service",
                                 itemId=theserviceApplication.service.pk, userId=request.user)
        return redirect('service-detail', pk=theserviceApplication.service.pk)


class DeactivateEventApplication(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        theeventApplication = EventApplication.objects.get(pk=pk)
        theeventApplication.isActive = False
        theeventApplication.save()
        notification = NotifyUser.objects.create(notify=theeventApplication.applicant, notification=str(
            request.user) + ' deactivated your application for event ' + str(theeventApplication.event.eventname) + '.',
                                                 offerType="event", offerPk=theeventApplication.event.pk)
        theeventApplication.applicant.profile.unreadcount = theeventApplication.applicant.profile.unreadcount + 1
        theeventApplication.applicant.profile.save()
        notification = NotifyUser.objects.create(notify=theeventApplication.event.eventcreater, notification=str(
            request.user) + ' deactivated the application of ' + str(
            theeventApplication.applicant) + ' for your event ' + str(theeventApplication.event.eventname) + '.',
                                                 offerType="event", offerPk=theeventApplication.event.pk)
        theeventApplication.event.eventcreater.profile.unreadcount = theeventApplication.event.eventcreater.profile.unreadcount + 1
        theeventApplication.event.eventcreater.profile.save()
        applicationsNext = EventApplication.objects.filter(event=theeventApplication.event).filter(
            approved=False).filter(isDeleted=False).filter(isActive=True).order_by('-date')
        count = 0
        for applicationNext in applicationsNext:
            if count == 0:
                applicationNext.approved = True
                applicationNext.save()
                count = 1
        log = Log.objects.create(operation="deactivateeventapplication", itemType="event",
                                 itemId=theeventApplication.event.pk, userId=request.user)
        return redirect('event-detail', pk=theeventApplication.event.pk)


class Deactivateds(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = Service.objects.filter(isActive=False)
        services_count = len(services)
        events = Event.objects.filter(isActive=False)
        events_count = len(events)
        profiles = UserProfile.objects.filter(isActive=False)
        profiles_count = len(profiles)
        context = {
            'services': services,
            'services_count': services_count,
            'events': events,
            'events_count': events_count,
            'profiles': profiles,
            'profiles_count': profiles_count,
        }
        return render(request, 'social/deactivateds.html', context)


class FeaturedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        featureds = Featured.objects.filter(itemType="service")
        services = []
        currentTime = timezone.now()
        for featured in featureds:
            serviceToAdd = Service.objects.get(pk=featured.itemId)
            services.append(serviceToAdd)
        services_count = len(services)
        context = {
            'services': services,
            'services_count': services_count,
            'currentTime': currentTime,
        }
        return render(request, 'social/featuredservices.html', context)


class FeaturedEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        featureds = Featured.objects.filter(itemType="event")
        events = []
        currentTime = timezone.now()
        for featured in featureds:
            eventToAdd = Event.objects.get(pk=featured.itemId)
            events.append(eventToAdd)
        events_count = len(events)
        context = {
            'events': events,
            'events_count': events_count,
            'currentTime': currentTime,
        }
        return render(request, 'social/featuredevents.html', context)


class AddServiceFeatured(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        featured = Featured.objects.create(itemType="service", itemId=pk)
        return redirect('service-detail', pk=pk)


class RemoveServiceFeatured(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        featured = Featured.objects.get(itemType="service", itemId=pk)
        featured.delete()
        return redirect('service-detail', pk=pk)


class AddEventFeatured(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        featured = Featured.objects.create(itemType="event", itemId=pk)
        return redirect('event-detail', pk=pk)


class RemoveEventFeatured(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        featured = Featured.objects.get(itemType="event", itemId=pk)
        featured.delete()
        return redirect('event-detail', pk=pk)
