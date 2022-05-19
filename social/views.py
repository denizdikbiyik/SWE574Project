from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import Lower
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from .models import Service, UserProfile, Event, ServiceApplication, UserRatings, NotifyUser, EventApplication, Tag, \
    Log, Communication, Like, UserComplaints, Featured, Interest, Search
from .forms import ServiceForm, EventForm, ServiceApplicationForm, RatingForm, EventApplicationForm, ProfileForm, \
    RequestForm, ComplaintForm, MyLocation, ComplaintFormAdmin
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib import messages, auth
from django.utils import timezone
from django.db.models import Avg, Q, F
from datetime import timedelta
from online_users.models import OnlineUserActivity
from datetime import datetime
import re
from random import randrange
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from geopy.distance import distance
from functools import reduce
import operator

# MatPlotLib
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
from geopy.geocoders import Nominatim

from operator import attrgetter

import pandas as pd
import matplotlib as mpl
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image


# Added by AT
def reverse_location(coordinates):
    geolocator = Nominatim(user_agent="swe574")
    r_location = geolocator.reverse(coordinates)
    return r_location.address


class ServiceCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            request.session["type"] = "service"
            form = ServiceForm()
            context = {
                'form': form,
            }
            return render(request, 'social/service_create.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
                        if new_service.capacity < 1 or new_service.duration < 1:
                            if new_service.capacity < 1:
                                messages.warning(request, 'Capacity cannot be less than 1.')
                            if new_service.duration < 1:
                                messages.warning(request, 'Duration cannot be less than 1.')
                        else:
                            new_service.creater = request.user
                            creater_user_profile.reservehour = creater_user_profile.reservehour + new_service.duration
                            creater_user_profile.save()
                            if new_service.category:
                                notification = NotifyUser.objects.create(notify=new_service.category.requester,
                                                                        notification=str(
                                                                            request.user) + ' created service with your request ' + str(
                                                                            new_service.category) + '.',
                                                                        offerType="request",
                                                                        offerPk=0)
                                notified_user = UserProfile.objects.get(pk=new_service.category.requester)
                                notified_user.unreadcount = notified_user.unreadcount + 1
                                notified_user.save()
                            # new_service.wiki_description = request.session['description']  #  this gives key error Added by AT
                            new_service.wiki_description = request.session.get("description")  # Added by AT
                            request.session['description'] = None  # Added by AT
                            new_service.address = reverse_location(new_service.location)  # Added by AT
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
        else:
            return redirect('index')


class AllServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class CreatedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class AppliedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class ServiceDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
                        if service.wiki_description is not None:
                            definitions = service.wiki_description.split("as ")
                            if len(Interest.objects.filter(user=request.user, wiki_description=definitions[1])) == 0:
                                new_interest = Interest.objects.create(user=request.user, name=definitions[0], wiki_description=definitions[1], implicit=True, origin='like')
                                new_interest.save()
                        notification = NotifyUser.objects.create(notify=service.creater, notification=str(
                            new_application.applicant) + ' applied to service ' + str(new_application.service.name)+'.',
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
        else:
            return redirect('index')


class ApplicationDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            service_pk = self.kwargs['service_pk']
            service = Service.objects.get(pk=service_pk)
            application = ServiceApplication.objects.get(pk=pk)
            applicant_user_profile = UserProfile.objects.get(pk=application.applicant.pk)
            service_creater_profile = UserProfile.objects.get(pk=service.creater.pk)
            applicant_user_profile.reservehour = applicant_user_profile.reservehour + service.duration
            applicant_user_profile.save()
            if request.user == application.applicant:
                notification = NotifyUser.objects.create(notify=service.creater, notification=str(
                    applicant_user_profile.user.username) + ' canceled application for service ' + str(service.name)+'.',
                                                        offerType="service", offerPk=service.pk)
                notified_user = UserProfile.objects.get(pk=service.creater)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
                application.deletionInfo = "cancel"
            elif request.user == application.service.creater:
                notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                    service_creater_profile.user.username) + ' rejected your application for service ' + str(service.name)+'.',
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
        else:
            return redirect('index')


class ApplicationEditView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            application = ServiceApplication.objects.get(pk=pk)
            if application.service.creater == request.user:
                form = ServiceApplicationForm(instance=application)
                context = {
                    'form': form,
                }
                return render(request, 'social/application_edit.html', context)
            else:
                return redirect('service-detail', pk=application.service.pk)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class ConfirmServiceTaken(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class ConfirmServiceGiven(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


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
        if request.user.profile.isActive:
            service = Service.objects.get(pk=pk)
            editLogs = Log.objects.filter(itemType="service").filter(itemId=pk).filter(operation="editservice")
            remaining = (service.servicedate - datetime.today()).total_seconds()
            if service.creater == request.user:
                if remaining > 86400 and len(editLogs) < 2:
                    form = ServiceForm(instance=service)
                    context = {
                        'form': form,
                    }
                    return render(request, 'social/service_edit.html', context)
                else:
                    if remaining <= 86400:
                        messages.warning(request, 'You cannot edit because less than 1 day left to service.')
                    if len(editLogs) >= 2:
                        messages.warning(request, 'You cannot edit because you reached edit limit 2.')
                    return redirect('service-detail', pk=service.pk)
            else:
                return redirect('service-detail', pk=service.pk)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
                        if edit_service.capacity < 1 or edit_service.duration < 1:
                            if edit_service.capacity < 1:
                                messages.warning(request, 'Capacity cannot be less than 1.')
                            if edit_service.duration < 1:
                                messages.warning(request, 'Duration cannot be less than 1.')
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
                            service.address=reverse_location(edit_service.location)
                            service.capacity = edit_service.capacity
                            service.duration = edit_service.duration
                            service.category = edit_service.category
                            service.save()
                            log = Log.objects.create(operation="editservice", itemType="service", itemId=service.pk,
                                                    userId=request.user)
                            messages.success(request, 'Service editing is successful.')
                            applications = ServiceApplication.objects.filter(service=service).filter(
                                isDeleted=False).filter(
                                isActive=True)
                            for application in applications:
                                notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                                    service.name) + ' which you applied is edited.', offerType="service",
                                                                        offerPk=service.pk)
                                notified_user = UserProfile.objects.get(pk=application.applicant)
                                notified_user.unreadcount = notified_user.unreadcount + 1
                                notified_user.save()
                else:
                    messages.warning(request, 'You cannot make this service which causes credit hours exceed 15.')
            context = {
                'form': form,
            }
            return render(request, 'social/service_edit.html', context)
        else:
            return redirect('index')


class ServiceDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            service = Service.objects.get(pk=pk)
            remaining = (service.servicedate - datetime.today()).total_seconds()
            if service.creater == request.user:
                if remaining > 86400:
                    form = ServiceForm(instance=service)
                    context = {
                        'form': form,
                    }
                    return render(request, 'social/service_delete.html', context)
                else:
                    messages.warning(request, 'You cannot delete because less than 1 day left to service.')
                    return redirect('service-detail', pk=service.pk)
            else:
                return redirect('service-detail', pk=service.pk)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class EventCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            request.session["type"] = "event"
            form = EventForm()
            context = {
                'form': form,
            }
            return render(request, 'social/event_create.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
                    if new_event.eventcapacity < 1 or new_event.eventduration < 1:
                        if new_event.eventcapacity < 1:
                            messages.warning(request, 'Capacity cannot be less than 1.')
                        if new_event.eventduration < 1:
                            messages.warning(request, 'Duration cannot be less than 1.')
                    else:
                        new_event.eventcreater = request.user
                        # new_event.event_wiki_description = request.session['description']  # gives key error Added by AT
                        new_event.event_wiki_description = request.session.get("description")  # Added by AT
                        request.session['description'] = None  # Added by AT
                        new_event.event_address = reverse_location(new_event.eventlocation)  # Added by AT
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
        else:
            return redirect('index')


class AllEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class CreatedEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class AppliedEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class EventApplicationDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            event_pk = self.kwargs['event_pk']
            event = Event.objects.get(pk=event_pk)
            application = EventApplication.objects.get(pk=pk)
            applicant_user_profile = UserProfile.objects.get(pk=application.applicant.pk)
            event_creater_profile = UserProfile.objects.get(pk=event.eventcreater.pk)
            if request.user == application.applicant:
                notification = NotifyUser.objects.create(notify=event.eventcreater, notification=str(
                    applicant_user_profile.user.username) + ' canceled application for event ' + str(event.eventname)+'.',
                                                        offerType="event", offerPk=event.pk)
                notified_user = UserProfile.objects.get(pk=event.eventcreater)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
                application.deletionInfo = "cancel"
            elif request.user == application.event.eventcreater:
                notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                    event_creater_profile.user.username) + ' rejected your application for event ' + str(event.eventname)+'.',
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
        else:
            return redirect('index')


class EventDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')

    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
                        new_application.applicant) + ' applied to event ' + str(new_application.event.eventname)+'.',
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
        else:
            return redirect('index')


class EventEditView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            event = Event.objects.get(pk=pk)
            editLogs = Log.objects.filter(itemType="event").filter(itemId=pk).filter(operation="editevent")
            remaining = (event.eventdate - datetime.today()).total_seconds()
            if event.eventcreater == request.user:
                if remaining > 86400 and len(editLogs) < 2:
                    form = EventForm(instance=event)
                    context = {
                        'form': form,
                    }
                    return render(request, 'social/event_edit.html', context)
                else:
                    if remaining <= 86400:
                        messages.warning(request, 'You cannot edit because less than 1 day left to event.')
                    if len(editLogs) >= 2:
                        messages.warning(request, 'You cannot edit because you reached edit limit 2.')
                    return redirect('event-detail', pk=event.pk)
            else:
                return redirect('event-detail', pk=event.pk)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            form = EventForm(request.POST, request.FILES)
            event = Event.objects.get(pk=pk)
            applications = EventApplication.objects.filter(event=event).filter(isDeleted=False).filter(isActive=True)
            number_of_accepted = len(applications.filter(approved=True))
            if form.is_valid():
                edit_event = form.save(commit=False)
                if edit_event.eventcapacity < number_of_accepted:
                    messages.warning(request, 'You cannot make the capacity below the accepted number.')
                else:
                    if edit_event.eventcapacity < 1 or edit_event.eventduration < 1:
                        if edit_event.eventcapacity < 1:
                            messages.warning(request, 'Capacity cannot be less than 1.')
                        if edit_event.eventduration < 1:
                            messages.warning(request, 'Duration cannot be less than 1.')
                    else:
                        event.eventpicture = event.eventpicture
                        if request.FILES:
                            event.eventpicture = edit_event.eventpicture
                        event.eventname = edit_event.eventname
                        event.eventdescription = edit_event.eventdescription
                        event.eventdate = edit_event.eventdate
                        event.eventlocation = edit_event.eventlocation
                        event.event_address = reverse_location(edit_event.eventlocation)
                        event.eventcapacity = edit_event.eventcapacity
                        event.eventduration = edit_event.eventduration
                        event.save()
                        log = Log.objects.create(operation="editevent", itemType="event", itemId=event.pk,
                                                userId=request.user)
                        messages.success(request, 'Event editing is successful.')
                        for application in applications:
                            notification = NotifyUser.objects.create(notify=application.applicant, notification=str(
                                event.eventname) + ' event which you applied is edited.', offerType="event",
                                                                    offerPk=event.pk)
                            notified_user = UserProfile.objects.get(pk=application.applicant)
                            notified_user.unreadcount = notified_user.unreadcount + 1
                            notified_user.save()
            context = {
                'form': form,
            }
            return render(request, 'social/event_edit.html', context)
        else:
            return redirect('index')


class EventDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            event = Event.objects.get(pk=pk)
            remaining = (event.eventdate - datetime.today()).total_seconds()
            if event.eventcreater == request.user:
                if remaining > 86400:
                    form = EventForm(instance=event)
                    context = {
                        'form': form,
                    }
                    return render(request, 'social/event_delete.html', context)
                else:
                    messages.warning(request, 'You cannot delete because less than 1 day left to event.')
                    return redirect('event-detail', pk=event.pk)
            else:
                return redirect('event-detail', pk=event.pk)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(pk=pk)
            user = profile.user
            followers = profile.followers.all()
            ratings_average = UserRatings.objects.filter(rated=profile.user).aggregate(Avg('rating'))
            interest = request.GET.get("deleted")
            if interest:
                Interest.objects.filter(user=user, wiki_description=interest, implicit=False).delete()

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
            interests = Interest.objects.filter(user=user)

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
                'interests': interests
            }
            return render(request, 'social/profile.html', context)
        else:
            return redirect('index')


class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(pk=pk)
            if profile.user == request.user:
                form = ProfileForm(instance=profile)
                context = {
                    'form': form,
                }
                return render(request, 'social/profile_edit.html', context)
            else:
                return redirect('profile', pk=profile.pk)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            follow_pk = self.kwargs['followpk']
            profile = UserProfile.objects.get(pk=follow_pk)
            profile.followers.add(request.user)
            log = Log.objects.create(operation="follow", itemType="user", itemId=follow_pk, userId=request.user)
            notification = NotifyUser.objects.create(notify=profile.user, notification=str(request.user) + ' followed you.',
                                                    offerType="user", offerPk=request.user.pk)
            notified_user = UserProfile.objects.get(pk=profile.user)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            return redirect('profile', pk=follow_pk)
        else:
            return redirect('index')


class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            follow_pk = self.kwargs['followpk']
            profile = UserProfile.objects.get(pk=follow_pk)
            profile.followers.remove(request.user)
            log = Log.objects.create(operation="unfollow", itemType="user", itemId=follow_pk, userId=request.user)
            return redirect('followings', pk=request.user.pk)
        else:
            return redirect('index')


class RemoveMyFollower(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            follower_pk = self.kwargs['follower_pk']
            follower = UserProfile.objects.get(pk=follower_pk).user
            profile = UserProfile.objects.get(pk=request.user.pk)
            profile.followers.remove(follower)
            log = Log.objects.create(operation="removemyfollower", itemType="user", itemId=follower_pk, userId=request.user)
            return redirect('followers', pk=request.user.pk)
        else:
            return redirect('index')


class FollowersListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(pk=pk)
            followers = profile.followers.all()
            number_of_followers = len(followers)
            context = {
                'followers': followers,
                'profile': profile,
                'number_of_followers': number_of_followers
            }
            return render(request, 'social/followers_list.html', context)
        else:
            return redirect('index')


class FollowingsListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class RateUser(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')

    def post(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class RateUserEdit(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            rating = UserRatings.objects.get(pk=pk)
            form = RatingForm(instance=rating)
            context = {
                'form': form,
                'rating': rating,
            }
            return render(request, 'social/rating-edit.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class RateUserDelete(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            rating = UserRatings.objects.get(pk=pk)
            form = RatingForm(instance=rating)
            context = {
                'form': form,
            }
            return render(request, 'social/rating-delete.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            rating = UserRatings.objects.get(pk=pk)
            service = rating.service
            log = Log.objects.create(operation="deleterating", itemType="service", itemId=rating.service.pk,
                                    affectedItemType="user", affectedItemId=rating.rated.pk, userId=request.user)
            rating.delete()
            return redirect('service-detail', pk=service.pk)
        else:
            return redirect('index')


class TimeLine(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            currentTime = timezone.now()
            profile = UserProfile.objects.get(user=request.user)
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
            logs = []
            for one in followedOnes:
                for service in services:
                    if service.creater == one.user:
                        services2.append(service)
                for event in events:
                    if event.eventcreater == one.user:
                        events2.append(event)
                allLogs = Log.objects.filter(userId=one.pk)
                for allLog in allLogs:
                    if allLog.operation == "createservice" or allLog.operation == "editservice" or allLog.operation == "deleteservice" or allLog.operation == "createserviceapplication" or allLog.operation == "deleteserviceapplication" or allLog.operation == "confirmtaken" or allLog.operation == "confirmgiven" or allLog.operation == "createevent" or allLog.operation == "editevent" or allLog.operation == "deleteevent" or allLog.operation == "createeventapplication" or allLog.operation == "deleteeventapplication" or allLog.operation == "follow" or allLog.operation == "unfollow" or allLog.operation == "like" or allLog.operation == "unlike":
                        if allLog.operation == "deleteserviceapplication" or allLog.operation == "deleteeventapplication":
                            if allLog.affectedItemId == allLog.userId:
                                logs.append(allLog)
                        else:
                            logs.append(allLog)

            allServices = Service.objects.all()
            allEvents = Event.objects.all()
            allUsers = UserProfile.objects.all()
            allServicesToClick = Service.objects.filter(isActive=True).filter(isDeleted=False)
            allEventsToClick = Event.objects.filter(isActive=True).filter(isDeleted=False)
            allUsersToClick = UserProfile.objects.filter(isActive=True)

            conversion = {'createservice': ' created service ',
                        'editservice': ' edited service ',
                        'deleteservice': ' deleted service ',
                        'createserviceapplication': ' applied for service ',
                        'deleteserviceapplication': ' canceled application for service ',
                        'confirmtaken': ' took service ',
                        'confirmgiven': ' gave service ',
                        'createevent': ' created event ',
                        'editevent': ' edited event ',
                        'deleteevent': ' deleted event ',
                        'createeventapplication': ' applied for event ',
                        'deleteeventapplication': ' canceled application for event ',
                        'follow': ' followed ',
                        'unfollow': ' unfollowed ',
                        'like': ' liked ',
                        'unlike': ' unliked '}
            for log in logs:
                log.operation = conversion[log.operation]

            log_count = len(logs)
            events_count = len(events2)
            services_count = len(services2)

            logs.sort(key=attrgetter('date'), reverse=True)

            context = {
                'services': services2,
                'events': events2,
                'services_count': services_count,
                'events_count': events_count,
                'currentTime': currentTime,
                'logs': logs,
                'log_count': log_count,
                'allServices': allServices,
                'allEvents': allEvents,
                'allUsers': allUsers,
                'allServicesToClick': allServicesToClick,
                'allEventsToClick': allEventsToClick,
                'allUsersToClick': allUsersToClick
            }
            return render(request, 'social/timeline.html', context)
        else:
            return redirect('index')


class ServiceSearch(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            request.session["search"] = "servicesearch"
            query = self.request.GET.get('query')
            sorting = self.request.GET.get('sorting')
            category = self.request.GET.get('category')  # For combining with ServiceFilter() AT
            cat_sel = category
            currentTime = timezone.now()

            services_query = Service.objects.filter(isDeleted=False).filter(isActive=True).filter(
                servicedate__gte=currentTime)

            if category == "all" or category == None:
                services_query = services_query
            else:
                services_query = services_query.filter(category__tag=category)

            if "query" in request.GET:
                if query == None or query == "":
                    services_query = services_query
                else:
                    services_address_pk = set()
                    for service in services_query:
                        address = service.address
                        if address:
                            if re.search(query, address, re.IGNORECASE):
                                services_address_pk.add(service.pk)
                    services_query = services_query.filter(
                        Q(name__icontains=query) | Q(description__icontains=query) | Q(
                            wiki_description__icontains=query) | Q(
                            address__icontains=query) | Q(pk__in=services_address_pk))
            else:
                query=""

            # Map
            message=""
            slocation = request.GET.get("slocation")
            if "slocation" in request.GET:
                if slocation == "map":
                    if request.session.get("target_location") !=None or request.session.get("distance") !=None:
                        target_location = str(request.session.get("target_location"))
                        distance_target = int(request.session.get("distance"))
                        services_location_pk = set()
                        for service in services_query:
                            service_location = service.location
                            if distance(target_location, service_location).km <= distance_target:
                                services_location_pk.add(service.pk)
                        services_query = services_query.filter(Q(pk__in=services_location_pk))
                    else:
                        message="Please choose a location from map."
                        services_query = services_query
                elif slocation == "home":
                    target_location = request.user.profile.location
                    services_location_for_home_pk = set()
                    for service in services_query:
                        service_location = service.location
                        if distance(target_location, service_location).km <= 10:
                            services_location_for_home_pk.add(service.pk)
                    services_query = services_query.filter(Q(pk__in=services_location_for_home_pk))
                else:
                    services_query = services_query
                    request.session["target_location"]=None
                    request.session["distance"]=None
            # End of Map

            services_sorted = []
            if "page" not in request.GET or request.session.get('services_sorted') is  None:
                if sorting == "newest":
                    services_sorted = services_query.order_by('createddate')
                elif sorting == "rating":
                    services_sorted = self.highest_rated_picked(list(services_query.order_by('createddate')))
                elif sorting == "name":
                    services_sorted = services_query.order_by(Lower("name"))
                elif sorting == "servicedate":
                    services_sorted = services_query.order_by("servicedate")
                else:
                    services = list(services_query)
                    i = 0
                    while i < len(services):
                        random_pick = randrange(4)
                        if random_pick == 0:
                            service = self.sub_date_picked(services)
                            services_sorted.append(service)
                            services.remove(service)
                        elif random_pick == 1:
                            service = self.rating_picked(services)
                            services_sorted.append(service)
                            services.remove(service)
                        elif random_pick == 2:
                            service = self.follow_status_picked(services, request.user.id)
                            services_sorted.append(service)
                            services.remove(service)
                        else:
                            service = self.interest_picked(services,
                                                           list(Interest.objects.filter(user=request.user.id)))
                            services_sorted.append(service)
                            services.remove(service)
                    # do not change the line below or do not remove from this else block
                    # if you write separated sorting code, the code below should be together with search result
                    # but not with sorting to not duplicate the log
                    if query != None:
                        if query.strip() != "":
                            searchLog = Search.objects.create(query=query.replace(" ", ""), searchType="service",
                                                              resultCount=len(services_sorted),
                                                              userId=request.user)
                    # end of the obligation
                    session_services = []
                    for service in services_sorted:
                        session_services.append(service.pk)
                    request.session['services_sorted'] = session_services
            else:
                for pk in request.session.get('services_sorted'):
                    service = Service.objects.get(pk=pk)
                    if service is not None:
                        services_sorted.append(service)

            services_count = len(services_sorted)
            alltags = Tag.objects.all()
            category_list = Tag.objects.values_list("tag", flat=True).distinct()
            # Pagination
            object_list = services_sorted
            page_num = request.GET.get('page', 1)
            paginator = Paginator(object_list, 10)
            try:
                page_obj = paginator.page(page_num)
            except PageNotAnInteger:
                # if page is not an integer, deliver the first page
                page_obj = paginator.page(1)
            except EmptyPage:
                # if the page is out of range, deliver the last page
                page_obj = paginator.page(paginator.num_pages)
            # End of Pagination

            context = {
                'page_obj': page_obj,
                'services_count': services_count,
                'currentTime': currentTime,
                'alltags': alltags,
                "cat_sel": cat_sel,
                "category_list": category_list,
                "sorting": sorting,
                "slocation": slocation,
                "message": message,
                "query": query,
            }
            return render(request, 'social/service-search.html', context)
        else:
            return redirect('index')

    def sub_date_picked(self, search_results):
        def sub_date_sorted(service):
            return service.creater.date_joined

        services_sub_date_sorted = sorted(search_results, reverse=True, key=sub_date_sorted)
        return services_sub_date_sorted[0]

    def rating_picked(self, search_results):
        ratings = []

        def rating_sorted(service):
            past_ratings = UserRatings.objects.filter(service=service)
            ratings_average = UserRatings.objects.filter(rated=service.creater).aggregate(Avg('rating'))['rating__avg']
            return ratings_average if (len(past_ratings) != 0) else 0

        for service in search_results:
            ratings.append(rating_sorted(service))

        services_rating_sorted = sorted(search_results, reverse=True, key=rating_sorted)

        num_of_services = ratings.count(ratings[0])
        if num_of_services > 1:
            return services_rating_sorted[randrange(num_of_services)]
        else:
            return services_rating_sorted[0]

    def follow_status_picked(self, search_results, searcher):
        follow_table = []

        def follow_status_sorted(service):
            profile = UserProfile.objects.get(pk=service.creater.id)
            followers = profile.followers.all()
            if searcher in followers:
                return 1
            else:
                return 0

        for service in search_results:
            follow_table.append(follow_status_sorted(service))

        services_follow_sorted = sorted(search_results, reverse=True, key=follow_status_sorted)

        num_of_services = follow_table.count(follow_table[0])
        if num_of_services > 1:
            return services_follow_sorted[randrange(num_of_services)]
        else:
            return services_follow_sorted[0]

    def interest_picked(self, search_results, user_interests):
        interest_table = []

        def interest_sorted(service):
            owner_interests = [interest.wiki_description for interest in
                               Interest.objects.filter(user=service.creater.id)]
            num_of_common_interests = 0
            for interest in user_interests:
                if interest.wiki_description in owner_interests:
                    num_of_common_interests += 1
            return num_of_common_interests

        for service in search_results:
            interest_table.append(interest_sorted(service))

        services_interest_sorted = sorted(search_results, reverse=True, key=interest_sorted)
        num_of_services = interest_table.count(interest_table[0])
        if num_of_services > 1:
            return services_interest_sorted[randrange(num_of_services)]
        else:
            return services_interest_sorted[0]

    def highest_rated_picked(self, search_results):
        ratings = []

        def rating_sorted(service):
            past_ratings = UserRatings.objects.filter(service=service)
            ratings_average = UserRatings.objects.filter(rated=service.creater).aggregate(Avg('rating'))['rating__avg']
            return ratings_average if (len(past_ratings) != 0) else 0

        for service in search_results:
            ratings.append(rating_sorted(service))

        return sorted(search_results, reverse=True, key=rating_sorted)


# Combined with ServiceSearch() and can be deleted. AT
class ServiceFilter(View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class EventSearch(View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            request.session["search"]="eventsearch"
            query = self.request.GET.get('query')
            sorting = self.request.GET.get('sorting')
            currentTime = timezone.now()

            events = Event.objects.filter(isDeleted=False).filter(isActive=True).filter(eventdate__gte=currentTime)

            if "query" in request.GET:
                events_pk = set()
                for event in events:
                    address = event.event_address
                    if address:
                        if re.search(query, address, re.IGNORECASE):
                            events_pk.add(event.pk)

                events =events.filter(
                    Q(eventname__icontains=query) | Q(eventdescription__icontains=query) | Q(
                        event_wiki_description__icontains=query) | Q(
                        event_address__icontains=query) | Q(pk__in=events_pk))
            else:
                events = events


            # Map
            message = ""
            slocation = request.GET.get("slocation")
            if "slocation" in request.GET:
                if slocation == "map":
                    if request.session.get("target_location") != None or request.session.get("distance") != None:
                        target_location = str(request.session.get("target_location"))
                        distance_target = int(request.session.get("distance"))
                        event_location_pk = set()
                        for event in events:
                            event_location = event.eventlocation
                            if distance(target_location, event_location).km <= distance_target:
                                event_location_pk.add(event.pk)
                        events = events.filter(Q(pk__in=event_location_pk))
                    else:
                        message = "Please choose a location from map."
                        events = events
                elif slocation == "home":
                    target_location = request.user.profile.location
                    event_location_for_home_pk = set()
                    for event in events:
                        event_location = event.eventlocation
                        if distance(target_location, event_location).km <= 10:
                            event_location_for_home_pk.add(event.pk)
                    events = events.filter(Q(pk__in=event_location_for_home_pk))
                else:
                    events = events
                    request.session["target_location"] = None
                    request.session["distance"] = None
            # End of Map

            if "sorting" in request.GET:
                if sorting == "createdate":
                    events=events.order_by("eventcreateddate")
                elif sorting == "name":
                    events = events.order_by(Lower("eventname"))
                else :
                    events = events.order_by("eventdate")


            events_count = len(events)

            # do not change the line below or do not remove from this block
            # if you write separated sorting code, the code below should be together with search result 
            # but not with sorting to not duplicate the log
            if query != None:
                if query.strip() != "":
                    searchLog = Search.objects.create(query=query.replace(" ", ""), searchType="event", resultCount=events_count, userId=request.user)
            # end of the obligation

            # Pagination
            object_list = events
            page_num = request.GET.get('page', 1)
            paginator = Paginator(object_list, 10)
            try:
                page_obj = paginator.page(page_num)
            except PageNotAnInteger:
                # if page is not an integer, deliver the first page
                page_obj = paginator.page(1)
            except EmptyPage:
                # if the page is out of range, deliver the last page
                page_obj = paginator.page(paginator.num_pages)
            # End of Pagination

            context = {
                'page_obj': page_obj,
                'events_count': events_count,
                'currentTime': currentTime,
                'sorting': sorting,
                'query': query,
                'message': message,
                'slocation': slocation,
            }

            return render(request, 'social/event-search.html', context)
        else:
            return redirect('index')


class SearchLogList(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            searchLogs = Search.objects.all()
            searchLogsServices = searchLogs.filter(searchType="service")
            searchLogsEvents = searchLogs.filter(searchType="event")
            searchLogsServices_count = len(searchLogsServices)
            searchLogsEvents_count = len(searchLogsEvents)
            context = {
                'searchLogs': searchLogs,
                'searchLogsServices': searchLogsServices,
                'searchLogsEvents': searchLogsEvents,
                'searchLogsServices_count': searchLogsServices_count,
                'searchLogsEvents_count': searchLogsEvents_count
            }
            return render(request, 'social/searchloglist.html', context)
        else:
            return redirect('index')


class SearchLogListZero(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            searchLogs = Search.objects.all()
            searchLogsServices = searchLogs.filter(searchType="service").filter(resultCount=0)
            searchLogsEvents = searchLogs.filter(searchType="event").filter(resultCount=0)
            searchLogsServices_count = len(searchLogsServices)
            searchLogsEvents_count = len(searchLogsEvents)
            context = {
                'searchLogs': searchLogs,
                'searchLogsServices': searchLogsServices,
                'searchLogsEvents': searchLogsEvents,
                'searchLogsServices_count': searchLogsServices_count,
                'searchLogsEvents_count': searchLogsEvents_count
            }
            return render(request, 'social/searchloglistzero.html', context)
        else:
            return redirect('index')


class SearchLogWordCloud(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            searchLogsServices = Search.objects.filter(searchType="service")
            showCloud = False

            logList = []
            for log in searchLogsServices:
                logList.append(log.query.replace(" ", ""))

            if len(logList) > 0:
                unique_string = (" ").join(logList)
                wordcloud = WordCloud(width=600, height=300).generate(unique_string)
                plt.figure(figsize=(13, 5))
                plt.imshow(wordcloud, aspect="auto")
                plt.axis("off")
                plt.savefig('media/searchlogwordcloud.png', dpi=100, bbox_inches='tight', pad_inches=0)
                showCloud = True

            context = {
                'showCloud': showCloud
            }
            return render(request, 'social/searchlogwordcloud.html', context)
        else:
            return redirect('index')


class Notifications(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            notifications = NotifyUser.objects.filter(notify=request.user).filter(hasRead=False).order_by('-date')
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
        else:
            return redirect('index')


class RequestCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            form = RequestForm()
            context = {
                'form': form,
            }
            return render(request, 'social/request_create.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            form = RequestForm(request.POST)
            if form.is_valid():
                new_request = form.save(commit=False)
                new_request.requester = request.user
                new_request.save()
                messages.success(request, 'Request creation is successful.')
                if (new_request.toPerson):
                    notification = NotifyUser.objects.create(notify=new_request.toPerson, notification=str(
                        new_request.requester.username) + ' requested service tag ' + str(new_request.tag)+'.',
                                                            offerType="request", offerPk=new_request.pk)
                    notified_user = UserProfile.objects.get(pk=new_request.toPerson)
                    notified_user.unreadcount = notified_user.unreadcount + 1
                    notified_user.save()
            context = {
                'form': form,
            }
            return render(request, 'social/request_create.html', context)
        else:
            return redirect('index')


class CreatedRequestsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            requests = Tag.objects.filter(requester=request.user)
            number_of_requests = len(requests)
            context = {
                'requests': requests,
                'number_of_requests': number_of_requests,
            }
            return render(request, 'social/createdrequests.html', context)
        else:
            return redirect('index')


class RequestsFromMeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            requests = Tag.objects.filter(toPerson=request.user)
            number_of_requests = len(requests)
            context = {
                'requests': requests,
                'number_of_requests': number_of_requests,
            }
            return render(request, 'social/requestsfromme.html', context)
        else:
            return redirect('index')


class RequestDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class RequestDeleteView(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            requestToDelete = Tag.objects.get(pk=pk)
            if requestToDelete.requester == request.user:
                form = RequestForm(instance=requestToDelete)
                context = {
                    'form': form,
                }
                return render(request, 'social/request_delete.html', context)
            else:
                return redirect('request-detail', pk=requestToDelete.pk)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class AllUsersView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            users = UserProfile.objects.filter(isActive=True)
            # Pagination
            object_list = users
            page_num = request.GET.get('page', 1)
            paginator = Paginator(object_list, 10)
            try:
                page_obj = paginator.page(page_num)
            except PageNotAnInteger:
                # if page is not an integer, deliver the first page
                page_obj = paginator.page(1)
            except EmptyPage:
                # if the page is out of range, deliver the last page
                page_obj = paginator.page(paginator.num_pages)
            # End of Pagination
            context = {
                'page_obj': page_obj,
                'users': users,
            }

            return render(request, 'social/allusers.html', context)
        else:
            return redirect('index')


class UsersServicesListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(pk=pk)
            services = Service.objects.filter(creater=profile.user).filter(isDeleted=False).filter(isActive=True)
            number_of_services = len(services)
            context = {
                'services': services,
                'profile': profile,
                'number_of_services': number_of_services
            }
            return render(request, 'social/usersservices.html', context)
        else:
            return redirect('index')


class UsersEventsListView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(pk=pk)
            events = Event.objects.filter(eventcreater=profile.user).filter(isDeleted=False).filter(isActive=True)
            number_of_events = len(events)
            context = {
                'events': events,
                'profile': profile,
                'number_of_events': number_of_events
            }
            return render(request, 'social/usersevents.html', context)
        else:
            return redirect('index')


class AddAdminView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(pk=pk)
            profile.isAdmin = True
            profile.save()
            log = Log.objects.create(operation="addadmin", itemType="user", itemId=pk, userId=request.user)
            notification = NotifyUser.objects.create(notify=profile.user,
                                                    notification=str(request.user) + ' added you as admin.',
                                                    offerType="user", offerPk=pk)
            profile.unreadcount = profile.unreadcount + 1
            profile.save()
            return redirect('profile', pk=pk)
        else:
            return redirect('index')


class RemoveAdminView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(pk=pk)
            profile.isAdmin = False
            profile.save()
            log = Log.objects.create(operation="removeadmin", itemType="user", itemId=pk, userId=request.user)
            notification = NotifyUser.objects.create(notify=profile.user,
                                                    notification=str(request.user) + ' removed you from admins list.',
                                                    offerType="user", offerPk=pk)
            profile.unreadcount = profile.unreadcount + 1
            profile.save()
            return redirect('profile', pk=pk)
        else:
            return redirect('index')


class DashboardEventDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            event = Event.objects.get(pk=pk)
            applications = EventApplication.objects.filter(event=pk).order_by('-date')
            number_of_accepted = len(applications.filter(approved=True))
            application_number = len(applications)
            logs = Log.objects.filter(itemType="event").filter(itemId=pk)
            conversion = {'createevent': 'Event is created.',
                        'createeventapplication': 'Applied to this event.',
                        'editevent': 'Event is edited.',
                        'deleteevent': 'Event is deleted.',
                        'editeventapplication': 'Application to this event is edited.',
                        'deleteeventapplication': 'Application to this event is removed.',
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
                'is_active': event.isActive,
                'application_number': application_number,
                'logs': logs,
                'isDeleted': event.isDeleted
            }
            return render(request, 'social/dashboard_event_detail.html', context)
        else:
            return redirect('index')


class DashboardUserDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(user=pk)
            service_applications = ServiceApplication.objects.filter(applicant=pk)
            service_application_number = len(service_applications)
            event_applications = EventApplication.objects.filter(applicant=pk)
            event_application_number = len(event_applications)
            services = Service.objects.filter(creater=pk)
            service_number = len(services)
            events = Event.objects.filter(eventcreater=pk)
            event_number = len(events)
            date_today = datetime.now()
            outdated_services = Service.objects.filter(servicedate__lte=date_today)
            outdated_events = Event.objects.filter(eventdate__lte=date_today)
            logs = Log.objects.filter(itemType="user").filter(itemId=pk)
            conversion = {'editprofile': 'Profile is edited.',
                        'follow': 'Profile is followed.',
                        'unfollow': 'Profile is unfollowed.',
                        'removemyfollower': 'Profile removed follower.',
                        'addadmin': 'Made admin.',
                        'removeadmin': 'Removed admin.',
                        'createcomplaint': 'Created complaint.',
                        'editcomplaint': 'Edited complaint.',
                        'deletecomplaint': 'Deleted complaint.',
                        'solvecomplaint': 'Solved complaint.',
                        'deactivate': 'Deactivated.',
                        'activate': 'Activated.'}
            for log in logs:
                log.operation = conversion[log.operation]
            context = {
                'profile': profile,
                'service_applications': service_applications,
                'service_application_number': service_application_number,
                'event_applications': event_applications,
                'event_application_number': event_application_number,
                'services': services,
                'service_number': service_number,
                'events': events,
                'event_number': event_number,
                'outdated_services': outdated_services,
                'outdated_events': outdated_events,
                'logs': logs
            }
            return render(request, 'social/dashboard_user_detail.html', context)
        else:
            return redirect('index')


class DashboardServiceDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            service = Service.objects.get(pk=pk)
            applications = ServiceApplication.objects.filter(service=pk).order_by('-date')
            number_of_accepted = len(applications.filter(approved=True))
            application_number = len(applications)
            logs = Log.objects.filter(itemType="service").filter(itemId=pk)
            conversion = {'createservice': 'Service is created.',
                        'createserviceapplication': 'Applied to this service.',
                        'editservice': 'Service is edited.',
                        'deleteservice': 'Service is deleted.',
                        'editserviceapplication': 'Application to this service is edited.',
                        'deleteserviceapplication': 'Application to this service is removed.',
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
                'is_active': service.isActive,
                'isDeleted': service.isDeleted,
                'application_number': application_number,
                'logs': logs
            }
            return render(request, 'social/dashboard_service_detail.html', context)
        else:
            return redirect('index')


class ServiceDetailCommunicationView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
                                                                service.name)+'.', offerType="service", offerPk=service.pk)
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
                                                                service.name)+'.', offerType="service", offerPk=service.pk)
                    notified_user = UserProfile.objects.get(pk=applicationToNotify.applicant)
                    notified_user.unreadcount = notified_user.unreadcount + 1
                    notified_user.save()
            return redirect('service-detail', pk=service.pk)
        else:
            return redirect('index')


class ServiceCommunicationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Communication
    template_name = 'social/service_communication_delete.html'

    def get_success_url(self):
        service_pk = self.kwargs['service_pk']
        service = Service.objects.get(pk=service_pk)
        communication = self.get_object()
        if self.request.user != service.creater:
            notification = NotifyUser.objects.create(notify=service.creater, notification=str(
                self.request.user) + ' deleted communication message on service ' + str(service.name)+'.',
                                                    offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=service.creater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
        approvedApplications = ServiceApplication.objects.filter(approved=True).filter(isDeleted=False).filter(
            isActive=True)
        for approvedApplication in approvedApplications:
            if self.request.user != approvedApplication.applicant:
                notification = NotifyUser.objects.create(notify=approvedApplication.applicant, notification=str(
                    self.request.user) + ' deleted communication message on service ' + str(service.name)+'.',
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
        if self.request.user.profile.isActive == False:
            isOK = False
        return isOK


class EventDetailCommunicationView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
                                                                event.eventname)+'.', offerType="event", offerPk=event.pk)
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
                                                                event.eventname)+'.', offerType="event", offerPk=event.pk)
                    notified_user = UserProfile.objects.get(pk=applicationToNotify.applicant)
                    notified_user.unreadcount = notified_user.unreadcount + 1
                    notified_user.save()
            return redirect('event-detail', pk=event.pk)
        else:
            return redirect('index')


class EventCommunicationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Communication
    template_name = 'social/event_communication_delete.html'

    def get_success_url(self):
        event_pk = self.kwargs['event_pk']
        event = Event.objects.get(pk=event_pk)
        communication = self.get_object()
        if self.request.user != event.eventcreater:
            notification = NotifyUser.objects.create(notify=event.eventcreater, notification=str(
                self.request.user) + ' deleted communication message on event ' + str(event.eventname)+'.',
                                                    offerType="event", offerPk=event.pk)
            notified_user = UserProfile.objects.get(pk=event.eventcreater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
        approvedApplications = EventApplication.objects.filter(approved=True).filter(isDeleted=False).filter(
            isActive=True)
        for approvedApplication in approvedApplications:
            if self.request.user != approvedApplication.applicant:
                notification = NotifyUser.objects.create(notify=approvedApplication.applicant, notification=str(
                    self.request.user) + ' deleted communication message on event ' + str(event.eventname)+'.',
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
        if self.request.user.profile.isActive == False:
            isOK = False
        return isOK


class ServiceLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            service = Service.objects.get(pk=pk)
            like = Like.objects.create(itemType="service", itemId=pk, liked=request.user)
            if service.wiki_description is not None:
                definitions = service.wiki_description.split("as ")
                if len(Interest.objects.filter(user=request.user, wiki_description=definitions[1])) == 0:
                    new_interest = Interest.objects.create(user=request.user, name=definitions[0], wiki_description=definitions[1], implicit= True, origin='like')
                    new_interest.save()
            notification = NotifyUser.objects.create(notify=service.creater,
                                                    notification=str(request.user) + ' liked service ' + str(service.name)+'.',
                                                    offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=service.creater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            log = Log.objects.create(operation="like", itemType="service", itemId=pk, userId=request.user)
            return redirect('service-detail', pk=pk)
        else:
            return redirect('index')


class ServiceUnlike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            service = Service.objects.get(pk=pk)
            like = Like.objects.get(itemType="service", itemId=pk, liked=request.user)
            like.delete()
            notification = NotifyUser.objects.create(notify=service.creater,
                                                    notification=str(request.user) + ' unliked service ' + str(
                                                        service.name)+'.', offerType="service", offerPk=service.pk)
            notified_user = UserProfile.objects.get(pk=service.creater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            log = Log.objects.create(operation="unlike", itemType="service", itemId=pk, userId=request.user)
            return redirect('service-detail', pk=pk)
        else:
            return redirect('index')


class EventLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            event = Event.objects.get(pk=pk)
            like = Like.objects.create(itemType="event", itemId=pk, liked=request.user)
            notification = NotifyUser.objects.create(notify=event.eventcreater,
                                                    notification=str(request.user) + ' liked event ' + str(
                                                        event.eventname)+'.', offerType="event", offerPk=event.pk)
            notified_user = UserProfile.objects.get(pk=event.eventcreater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            log = Log.objects.create(operation="like", itemType="event", itemId=pk, userId=request.user)
            return redirect('event-detail', pk=pk)
        else:
            return redirect('index')


class EventUnlike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            event = Event.objects.get(pk=pk)
            like = Like.objects.get(itemType="event", itemId=pk, liked=request.user)
            like.delete()
            notification = NotifyUser.objects.create(notify=event.eventcreater,
                                                    notification=str(request.user) + ' unliked event ' + str(
                                                        event.eventname)+'.', offerType="event", offerPk=event.pk)
            notified_user = UserProfile.objects.get(pk=event.eventcreater)
            notified_user.unreadcount = notified_user.unreadcount + 1
            notified_user.save()
            log = Log.objects.create(operation="unlike", itemType="event", itemId=pk, userId=request.user)
            return redirect('event-detail', pk=pk)
        else:
            return redirect('index')


class ServiceLikesList(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            service = Service.objects.get(pk=pk)
            likes = Like.objects.filter(itemType="service").filter(itemId=pk)
            likesCount = len(likes)
            context = {
                'likes': likes,
                'likesCount': likesCount,
                'service': service
            }
            return render(request, 'social/service_like_list.html', context)
        else:
            return redirect('index')


class EventLikesList(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            event = Event.objects.get(pk=pk)
            likes = Like.objects.filter(itemType="event").filter(itemId=pk)
            likesCount = len(likes)
            context = {
                'likes': likes,
                'likesCount': likesCount,
                'event': event
            }
            return render(request, 'social/event_like_list.html', context)
        else:
            return redirect('index')


class MyLikes(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct, v=val)

    return my_autopct


class AdminDashboardIndex(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            # user_activity_objects_15min = OnlineUserActivity.get_user_activities()
            # number_of_active_users_15min = user_activity_objects_15min.count()

            # user_activity_objects_60min = OnlineUserActivity.get_user_activities(timedelta(minutes=60))
            # users_60min = (user for user in user_activity_objects_60min)

            user_activity_objects = OnlineUserActivity.get_user_activities(timedelta(seconds=60))
            number_of_active_users = user_activity_objects.count()
            activeUsers = (user for user in user_activity_objects)

            allUsers = UserProfile.objects.all()
            allUsersCount = len(allUsers) - number_of_active_users

            labels = []
            data = []

            labels.append("Not Online Users")
            labels.append("Online Users")

            data.append(allUsersCount)
            data.append(number_of_active_users)

            explode = (0.1, 0)  # only "explode" the 2nd slice
            fig1, ax1 = plt.subplots()
            # ax1.pie(data, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            # ax1.pie(data, explode=explode, labels=labels, autopct=lambda p: '{:.0f}'.format(p * sum(data) / 100), shadow=True, startangle=90)
            ax1.pie(data, explode=explode, labels=labels, autopct=make_autopct(data), shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('Current Online Users: ' + str(number_of_active_users) + ' (click to see the list)', color='blue')
            plt.savefig('media/users_chart.png', dpi=100)

            weekday = datetime.today().weekday()
            if weekday == 0:
                days = ["Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon"]
            elif weekday == 1:
                days = ["Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue"]
            elif weekday == 2:
                days = ["Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed"]
            elif weekday == 3:
                days = ["Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"]
            elif weekday == 4:
                days = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
            elif weekday == 5:
                days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            else:
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

            serviceNum = []
            serviceApplicationNum = []
            eventNum = []
            eventApplicationNum = []

            minOneServicesApplication = ServiceApplication.objects.all()
            minTwoServicesApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=1)).date())
            minThreeServicesApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=2)).date())
            minFourServicesApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=3)).date())
            minFiveServicesApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=4)).date())
            minSixServicesApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=5)).date())
            minSevenServicesApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=6)).date())
            minEightServicesApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=7)).date())
            serviceApplicationNum.append(len(minSevenServicesApplication) - len(minEightServicesApplication))
            serviceApplicationNum.append(len(minSixServicesApplication) - len(minSevenServicesApplication))
            serviceApplicationNum.append(len(minFiveServicesApplication) - len(minSixServicesApplication))
            serviceApplicationNum.append(len(minFourServicesApplication) - len(minFiveServicesApplication))
            serviceApplicationNum.append(len(minThreeServicesApplication) - len(minFourServicesApplication))
            serviceApplicationNum.append(len(minTwoServicesApplication) - len(minThreeServicesApplication))
            serviceApplicationNum.append(len(minOneServicesApplication) - len(minTwoServicesApplication))

            minOneServices = Service.objects.all()
            minTwoServices = Service.objects.filter(createddate__lte=(datetime.now() - timedelta(days=1)).date())
            minThreeServices = Service.objects.filter(createddate__lte=(datetime.now() - timedelta(days=2)).date())
            minFourServices = Service.objects.filter(createddate__lte=(datetime.now() - timedelta(days=3)).date())
            minFiveServices = Service.objects.filter(createddate__lte=(datetime.now() - timedelta(days=4)).date())
            minSixServices = Service.objects.filter(createddate__lte=(datetime.now() - timedelta(days=5)).date())
            minSevenServices = Service.objects.filter(createddate__lte=(datetime.now() - timedelta(days=6)).date())
            minEightServices = Service.objects.filter(createddate__lte=(datetime.now() - timedelta(days=7)).date())
            serviceNum.append(len(minSevenServices) - len(minEightServices))
            serviceNum.append(len(minSixServices) - len(minSevenServices))
            serviceNum.append(len(minFiveServices) - len(minSixServices))
            serviceNum.append(len(minFourServices) - len(minFiveServices))
            serviceNum.append(len(minThreeServices) - len(minFourServices))
            serviceNum.append(len(minTwoServices) - len(minThreeServices))
            serviceNum.append(len(minOneServices) - len(minTwoServices))

            plt.clf()
            plt.plot(days, serviceNum, 'b', label='services')
            plt.plot(days, serviceApplicationNum, 'y', label='service applications')
            plt.legend()
            plt.grid(True)
            plt.title('Services and Service Application Creations in One Week')
            plt.savefig('media/services_chart.png', dpi=100)

            minOneEventsApplication = EventApplication.objects.all()
            minTwoEventsApplication = EventApplication.objects.filter(date__lte=(datetime.now() - timedelta(days=1)).date())
            minThreeEventsApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=2)).date())
            minFourEventsApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=3)).date())
            minFiveEventsApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=4)).date())
            minSixEventsApplication = EventApplication.objects.filter(date__lte=(datetime.now() - timedelta(days=5)).date())
            minSevenEventsApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=6)).date())
            minEightEventsApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - timedelta(days=7)).date())
            eventApplicationNum.append(len(minSevenEventsApplication) - len(minEightEventsApplication))
            eventApplicationNum.append(len(minSixEventsApplication) - len(minSevenEventsApplication))
            eventApplicationNum.append(len(minFiveEventsApplication) - len(minSixEventsApplication))
            eventApplicationNum.append(len(minFourEventsApplication) - len(minFiveEventsApplication))
            eventApplicationNum.append(len(minThreeEventsApplication) - len(minFourEventsApplication))
            eventApplicationNum.append(len(minTwoEventsApplication) - len(minThreeEventsApplication))
            eventApplicationNum.append(len(minOneEventsApplication) - len(minTwoEventsApplication))

            minOneEvents = Event.objects.all()
            minTwoEvents = Event.objects.filter(eventcreateddate__lte=(datetime.now() - timedelta(days=1)).date())
            minThreeEvents = Event.objects.filter(eventcreateddate__lte=(datetime.now() - timedelta(days=2)).date())
            minFourEvents = Event.objects.filter(eventcreateddate__lte=(datetime.now() - timedelta(days=3)).date())
            minFiveEvents = Event.objects.filter(eventcreateddate__lte=(datetime.now() - timedelta(days=4)).date())
            minSixEvents = Event.objects.filter(eventcreateddate__lte=(datetime.now() - timedelta(days=5)).date())
            minSevenEvents = Event.objects.filter(eventcreateddate__lte=(datetime.now() - timedelta(days=6)).date())
            minEightEvents = Event.objects.filter(eventcreateddate__lte=(datetime.now() - timedelta(days=7)).date())
            eventNum.append(len(minSevenEvents) - len(minEightEvents))
            eventNum.append(len(minSixEvents) - len(minSevenEvents))
            eventNum.append(len(minFiveEvents) - len(minSixEvents))
            eventNum.append(len(minFourEvents) - len(minFiveEvents))
            eventNum.append(len(minThreeEvents) - len(minFourEvents))
            eventNum.append(len(minTwoEvents) - len(minThreeEvents))
            eventNum.append(len(minOneEvents) - len(minTwoEvents))

            plt.clf()
            plt.plot(days, eventNum, 'm', label='events')
            plt.plot(days, eventApplicationNum, 'c', label='event applications')
            plt.legend()
            plt.grid(True)
            plt.title('Events and Event Application Creations in One Week')
            plt.savefig('media/events_chart.png', dpi=100)

            handServiceNum = []
            acceptedServiceApplications = []

            handOneServices = Service.objects.filter(is_given=True).filter(is_taken=True)
            handTwoServices = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - timedelta(days=1)).date())
            handThreeServices = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - timedelta(days=2)).date())
            handFourServices = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - timedelta(days=3)).date())
            handFiveServices = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - timedelta(days=4)).date())
            handSixServices = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - timedelta(days=5)).date())
            handSevenServices = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - timedelta(days=6)).date())
            handEightServices = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - timedelta(days=7)).date())
            handServiceNum.append(len(handSevenServices) - len(handEightServices))
            handServiceNum.append(len(handSixServices) - len(handSevenServices))
            handServiceNum.append(len(handFiveServices) - len(handSixServices))
            handServiceNum.append(len(handFourServices) - len(handFiveServices))
            handServiceNum.append(len(handThreeServices) - len(handFourServices))
            handServiceNum.append(len(handTwoServices) - len(handThreeServices))
            handServiceNum.append(len(handOneServices) - len(handTwoServices))

            acceptedOneServiceApplications = ServiceApplication.objects.filter(approved=True)
            acceptedTwoServiceApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - timedelta(days=1)).date())
            acceptedThreeServiceApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - timedelta(days=2)).date())
            acceptedFourServiceApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - timedelta(days=3)).date())
            acceptedFiveServiceApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - timedelta(days=4)).date())
            acceptedSixServiceApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - timedelta(days=5)).date())
            acceptedSevenServiceApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - timedelta(days=6)).date())
            acceptedEightServiceApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - timedelta(days=7)).date())
            acceptedServiceApplications.append(
                len(acceptedSevenServiceApplications) - len(acceptedEightServiceApplications))
            acceptedServiceApplications.append(len(acceptedSixServiceApplications) - len(acceptedSevenServiceApplications))
            acceptedServiceApplications.append(len(acceptedFiveServiceApplications) - len(acceptedSixServiceApplications))
            acceptedServiceApplications.append(len(acceptedFourServiceApplications) - len(acceptedFiveServiceApplications))
            acceptedServiceApplications.append(len(acceptedThreeServiceApplications) - len(acceptedFourServiceApplications))
            acceptedServiceApplications.append(len(acceptedTwoServiceApplications) - len(acceptedThreeServiceApplications))
            acceptedServiceApplications.append(len(acceptedOneServiceApplications) - len(acceptedTwoServiceApplications))

            plt.clf()
            plt.plot(days, handServiceNum, 'g', label='handshaken services')
            plt.plot(days, acceptedServiceApplications, 'r', label='accepted service applications')
            plt.legend()
            plt.grid(True)
            plt.title('Service Occurrance in One Week')
            plt.savefig('media/handshaken_services_chart.png', dpi=100)

            month = datetime.now().strftime('%B')
            if month == "January":
                months = ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
            elif month == "February":
                months = ["Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb"]
            elif month == "March":
                months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
            elif month == "April":
                months = ["May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
            elif month == "May":
                months = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"]
            elif month == "June":
                months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            elif month == "July":
                months = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
            elif month == "August":
                months = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
            elif month == "September":
                months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
            elif month == "October":
                months = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
            elif month == "November":
                months = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
            else:
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

            serviceMonthNum = []
            serviceApplicationMonthNum = []
            eventMonthNum = []
            eventApplicationMonthNum = []

            minOneServicesMonthApplication = ServiceApplication.objects.all()
            minTwoServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=1)).date())
            minThreeServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=2)).date())
            minFourServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=3)).date())
            minFiveServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=4)).date())
            minSixServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=5)).date())
            minSevenServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=6)).date())
            minEightServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=7)).date())
            minNineServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=8)).date())
            minTenServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=9)).date())
            minElevenServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=10)).date())
            minTwelveServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=11)).date())
            minThirteenServicesMonthApplication = ServiceApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=12)).date())
            serviceApplicationMonthNum.append(
                len(minTwelveServicesMonthApplication) - len(minThirteenServicesMonthApplication))
            serviceApplicationMonthNum.append(
                len(minElevenServicesMonthApplication) - len(minTwelveServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minTenServicesMonthApplication) - len(minElevenServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minNineServicesMonthApplication) - len(minTenServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minEightServicesMonthApplication) - len(minNineServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minSevenServicesMonthApplication) - len(minEightServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minSixServicesMonthApplication) - len(minSevenServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minFiveServicesMonthApplication) - len(minSixServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minFourServicesMonthApplication) - len(minFiveServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minThreeServicesMonthApplication) - len(minFourServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minTwoServicesMonthApplication) - len(minThreeServicesMonthApplication))
            serviceApplicationMonthNum.append(len(minOneServicesMonthApplication) - len(minTwoServicesMonthApplication))

            minOneServicesMonth = Service.objects.all()
            minTwoServicesMonth = Service.objects.filter(createddate__lte=(datetime.now() - relativedelta(months=1)).date())
            minThreeServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=2)).date())
            minFourServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=3)).date())
            minFiveServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=4)).date())
            minSixServicesMonth = Service.objects.filter(createddate__lte=(datetime.now() - relativedelta(months=5)).date())
            minSevenServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=6)).date())
            minEightServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=7)).date())
            minNineServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=8)).date())
            minTenServicesMonth = Service.objects.filter(createddate__lte=(datetime.now() - relativedelta(months=9)).date())
            minElevenServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=10)).date())
            minTwelveServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=11)).date())
            minThirteenServicesMonth = Service.objects.filter(
                createddate__lte=(datetime.now() - relativedelta(months=12)).date())
            serviceMonthNum.append(len(minTwelveServicesMonth) - len(minThirteenServicesMonth))
            serviceMonthNum.append(len(minElevenServicesMonth) - len(minTwelveServicesMonth))
            serviceMonthNum.append(len(minTenServicesMonth) - len(minElevenServicesMonth))
            serviceMonthNum.append(len(minNineServicesMonth) - len(minTenServicesMonth))
            serviceMonthNum.append(len(minEightServicesMonth) - len(minNineServicesMonth))
            serviceMonthNum.append(len(minSevenServicesMonth) - len(minEightServicesMonth))
            serviceMonthNum.append(len(minSixServicesMonth) - len(minSevenServicesMonth))
            serviceMonthNum.append(len(minFiveServicesMonth) - len(minSixServicesMonth))
            serviceMonthNum.append(len(minFourServicesMonth) - len(minFiveServicesMonth))
            serviceMonthNum.append(len(minThreeServicesMonth) - len(minFourServicesMonth))
            serviceMonthNum.append(len(minTwoServicesMonth) - len(minThreeServicesMonth))
            serviceMonthNum.append(len(minOneServicesMonth) - len(minTwoServicesMonth))

            plt.clf()
            plt.plot(months, serviceMonthNum, 'b', label='services')
            plt.plot(months, serviceApplicationMonthNum, 'y', label='service applications')
            plt.legend()
            plt.grid(True)
            plt.title('Services and Service Application Creations in One Year')
            plt.savefig('media/services_month_chart.png', dpi=100)

            minOneEventsMonthApplication = EventApplication.objects.all()
            minTwoEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=1)).date())
            minThreeEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=2)).date())
            minFourEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=3)).date())
            minFiveEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=4)).date())
            minSixEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=5)).date())
            minSevenEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=6)).date())
            minEightEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=7)).date())
            minNineEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=8)).date())
            minTenEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=9)).date())
            minElevenEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=10)).date())
            minTwelveEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=11)).date())
            minThirteenEventsMonthApplication = EventApplication.objects.filter(
                date__lte=(datetime.now() - relativedelta(months=12)).date())
            eventApplicationMonthNum.append(len(minTwelveEventsMonthApplication) - len(minThirteenEventsMonthApplication))
            eventApplicationMonthNum.append(len(minElevenEventsMonthApplication) - len(minTwelveEventsMonthApplication))
            eventApplicationMonthNum.append(len(minTenEventsMonthApplication) - len(minElevenEventsMonthApplication))
            eventApplicationMonthNum.append(len(minNineEventsMonthApplication) - len(minTenEventsMonthApplication))
            eventApplicationMonthNum.append(len(minEightEventsMonthApplication) - len(minNineEventsMonthApplication))
            eventApplicationMonthNum.append(len(minSevenEventsMonthApplication) - len(minEightEventsMonthApplication))
            eventApplicationMonthNum.append(len(minSixEventsMonthApplication) - len(minSevenEventsMonthApplication))
            eventApplicationMonthNum.append(len(minFiveEventsMonthApplication) - len(minSixEventsMonthApplication))
            eventApplicationMonthNum.append(len(minFourEventsMonthApplication) - len(minFiveEventsMonthApplication))
            eventApplicationMonthNum.append(len(minThreeEventsMonthApplication) - len(minFourEventsMonthApplication))
            eventApplicationMonthNum.append(len(minTwoEventsMonthApplication) - len(minThreeEventsMonthApplication))
            eventApplicationMonthNum.append(len(minOneEventsMonthApplication) - len(minTwoEventsMonthApplication))

            minOneEventsMonth = Event.objects.all()
            minTwoEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=1)).date())
            minThreeEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=2)).date())
            minFourEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=3)).date())
            minFiveEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=4)).date())
            minSixEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=5)).date())
            minSevenEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=6)).date())
            minEightEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=7)).date())
            minNineEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=8)).date())
            minTenEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=9)).date())
            minElevenEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=10)).date())
            minTwelveEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=11)).date())
            minThirteenEventsMonth = Event.objects.filter(
                eventcreateddate__lte=(datetime.now() - relativedelta(months=12)).date())
            eventMonthNum.append(len(minTwelveEventsMonth) - len(minThirteenEventsMonth))
            eventMonthNum.append(len(minElevenEventsMonth) - len(minTwelveEventsMonth))
            eventMonthNum.append(len(minTenEventsMonth) - len(minElevenEventsMonth))
            eventMonthNum.append(len(minNineEventsMonth) - len(minTenEventsMonth))
            eventMonthNum.append(len(minEightEventsMonth) - len(minNineEventsMonth))
            eventMonthNum.append(len(minSevenEventsMonth) - len(minEightEventsMonth))
            eventMonthNum.append(len(minSixEventsMonth) - len(minSevenEventsMonth))
            eventMonthNum.append(len(minFiveEventsMonth) - len(minSixEventsMonth))
            eventMonthNum.append(len(minFourEventsMonth) - len(minFiveEventsMonth))
            eventMonthNum.append(len(minThreeEventsMonth) - len(minFourEventsMonth))
            eventMonthNum.append(len(minTwoEventsMonth) - len(minThreeEventsMonth))
            eventMonthNum.append(len(minOneEventsMonth) - len(minTwoEventsMonth))

            plt.clf()
            plt.plot(months, eventMonthNum, 'm', label='events')
            plt.plot(months, eventApplicationMonthNum, 'c', label='event applications')
            plt.legend()
            plt.grid(True)
            plt.title('Events and Event Application Creations in One Year')
            plt.savefig('media/events_month_chart.png', dpi=100)

            handServiceMonthNum = []
            acceptedServiceMonthApplications = []

            handOneServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True)
            handTwoServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=1)).date())
            handThreeServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=2)).date())
            handFourServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=3)).date())
            handFiveServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=4)).date())
            handSixServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=5)).date())
            handSevenServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=6)).date())
            handEightServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=7)).date())
            handNineServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=8)).date())
            handTenServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=9)).date())
            handElevenServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=10)).date())
            handTwelveServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=11)).date())
            handThirteenServicesMonth = Service.objects.filter(is_given=True).filter(is_taken=True).filter(
                createddate__lte=(datetime.now() - relativedelta(months=12)).date())
            handServiceMonthNum.append(len(handTwelveServicesMonth) - len(handThirteenServicesMonth))
            handServiceMonthNum.append(len(handElevenServicesMonth) - len(handTwelveServicesMonth))
            handServiceMonthNum.append(len(handTenServicesMonth) - len(handElevenServicesMonth))
            handServiceMonthNum.append(len(handNineServicesMonth) - len(handTenServicesMonth))
            handServiceMonthNum.append(len(handEightServicesMonth) - len(handNineServicesMonth))
            handServiceMonthNum.append(len(handSevenServicesMonth) - len(handEightServicesMonth))
            handServiceMonthNum.append(len(handSixServicesMonth) - len(handSevenServicesMonth))
            handServiceMonthNum.append(len(handFiveServicesMonth) - len(handSixServicesMonth))
            handServiceMonthNum.append(len(handFourServicesMonth) - len(handFiveServicesMonth))
            handServiceMonthNum.append(len(handThreeServicesMonth) - len(handFourServicesMonth))
            handServiceMonthNum.append(len(handTwoServicesMonth) - len(handThreeServicesMonth))
            handServiceMonthNum.append(len(handOneServicesMonth) - len(handTwoServicesMonth))

            acceptedOneServiceMonthApplications = ServiceApplication.objects.filter(approved=True)
            acceptedTwoServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=1)).date())
            acceptedThreeServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=2)).date())
            acceptedFourServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=3)).date())
            acceptedFiveServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=4)).date())
            acceptedSixServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=5)).date())
            acceptedSevenServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=6)).date())
            acceptedEightServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=7)).date())
            acceptedNineServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=8)).date())
            acceptedTenServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=9)).date())
            acceptedElevenServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=10)).date())
            acceptedTwelveServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=11)).date())
            acceptedThirteenServiceMonthApplications = ServiceApplication.objects.filter(approved=True).filter(
                date__lte=(datetime.now() - relativedelta(months=12)).date())
            acceptedServiceMonthApplications.append(
                len(acceptedTwelveServiceMonthApplications) - len(acceptedThirteenServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedElevenServiceMonthApplications) - len(acceptedTwelveServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedTenServiceMonthApplications) - len(acceptedElevenServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedNineServiceMonthApplications) - len(acceptedTenServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedEightServiceMonthApplications) - len(acceptedNineServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedSevenServiceMonthApplications) - len(acceptedEightServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedSixServiceMonthApplications) - len(acceptedSevenServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedFiveServiceMonthApplications) - len(acceptedSixServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedFourServiceMonthApplications) - len(acceptedFiveServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedThreeServiceMonthApplications) - len(acceptedFourServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedTwoServiceMonthApplications) - len(acceptedThreeServiceMonthApplications))
            acceptedServiceMonthApplications.append(
                len(acceptedOneServiceMonthApplications) - len(acceptedTwoServiceMonthApplications))

            plt.clf()
            plt.plot(months, handServiceMonthNum, 'g', label='handshaken services')
            plt.plot(months, acceptedServiceMonthApplications, 'r', label='accepted service applications')
            plt.legend()
            plt.grid(True)
            plt.title('Service Occurrance in One Year')
            plt.savefig('media/handshaken_month_services_chart.png', dpi=100)

            userMonthNum = []

            minOneUsersMonth = User.objects.all()
            minTwoUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=1)).date())
            minThreeUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=2)).date())
            minFourUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=3)).date())
            minFiveUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=4)).date())
            minSixUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=5)).date())
            minSevenUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=6)).date())
            minEightUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=7)).date())
            minNineUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=8)).date())
            minTenUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=9)).date())
            minElevenUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=10)).date())
            minTwelveUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=11)).date())
            minThirteenUsersMonth = User.objects.filter(date_joined__lte=(datetime.now() - relativedelta(months=12)).date())
            userMonthNum.append(len(minTwelveUsersMonth) - len(minThirteenUsersMonth))
            userMonthNum.append(len(minElevenUsersMonth) - len(minTwelveUsersMonth))
            userMonthNum.append(len(minTenUsersMonth) - len(minElevenUsersMonth))
            userMonthNum.append(len(minNineUsersMonth) - len(minTenUsersMonth))
            userMonthNum.append(len(minEightUsersMonth) - len(minNineUsersMonth))
            userMonthNum.append(len(minSevenUsersMonth) - len(minEightUsersMonth))
            userMonthNum.append(len(minSixUsersMonth) - len(minSevenUsersMonth))
            userMonthNum.append(len(minFiveUsersMonth) - len(minSixUsersMonth))
            userMonthNum.append(len(minFourUsersMonth) - len(minFiveUsersMonth))
            userMonthNum.append(len(minThreeUsersMonth) - len(minFourUsersMonth))
            userMonthNum.append(len(minTwoUsersMonth) - len(minThreeUsersMonth))
            userMonthNum.append(len(minOneUsersMonth) - len(minTwoUsersMonth))

            plt.clf()
            plt.plot(months, userMonthNum, 'g', label='users')
            plt.legend()
            plt.grid(True)
            plt.title('User Creations in One Year')
            plt.savefig('media/users_month_chart.png', dpi=100)

            operationMonthNum = []

            minOneOperationsMonth = Log.objects.all()
            minTwoOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=1)).date())
            minThreeOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=2)).date())
            minFourOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=3)).date())
            minFiveOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=4)).date())
            minSixOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=5)).date())
            minSevenOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=6)).date())
            minEightOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=7)).date())
            minNineOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=8)).date())
            minTenOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=9)).date())
            minElevenOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=10)).date())
            minTwelveOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=11)).date())
            minThirteenOperationsMonth = Log.objects.filter(date__lte=(datetime.now() - relativedelta(months=12)).date())
            operationMonthNum.append(len(minTwelveOperationsMonth) - len(minThirteenOperationsMonth))
            operationMonthNum.append(len(minElevenOperationsMonth) - len(minTwelveOperationsMonth))
            operationMonthNum.append(len(minTenOperationsMonth) - len(minElevenOperationsMonth))
            operationMonthNum.append(len(minNineOperationsMonth) - len(minTenOperationsMonth))
            operationMonthNum.append(len(minEightOperationsMonth) - len(minNineOperationsMonth))
            operationMonthNum.append(len(minSevenOperationsMonth) - len(minEightOperationsMonth))
            operationMonthNum.append(len(minSixOperationsMonth) - len(minSevenOperationsMonth))
            operationMonthNum.append(len(minFiveOperationsMonth) - len(minSixOperationsMonth))
            operationMonthNum.append(len(minFourOperationsMonth) - len(minFiveOperationsMonth))
            operationMonthNum.append(len(minThreeOperationsMonth) - len(minFourOperationsMonth))
            operationMonthNum.append(len(minTwoOperationsMonth) - len(minThreeOperationsMonth))
            operationMonthNum.append(len(minOneOperationsMonth) - len(minTwoOperationsMonth))

            plt.clf()
            plt.plot(months, operationMonthNum, 'g', label='operations')
            plt.legend()
            plt.grid(True)
            plt.title('Operation on the CommUnity in One Year')
            plt.savefig('media/operations_month_chart.png', dpi=100)

            context = {
                'activeUsers': activeUsers,
                'number_of_active_users': number_of_active_users,
                'allUsers': allUsers,
                'allUsersCount': allUsersCount,
            }
            return render(request, 'social/admindashboardindex.html', context)
        else:
            return redirect('index')


class OnlineUsersList(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class ComplaintUser(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            form = ComplaintForm()
            complainted = UserProfile.objects.get(user=pk)
            complaintRecord = UserComplaints.objects.filter(complainted=complainted.user).filter(
                complainter=request.user).filter(isDeleted=False).filter(isSolved=False)
            isComplainted = len(complaintRecord)
            context = {
                'form': form,
                'complaintRecord': complaintRecord,
                'isComplainted': isComplainted,
                'complainted': complainted,
            }
            return render(request, 'social/complaint.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
                                                            notification=str(request.user) + ' created complaint about ' + str(
                                                                complainted.user)+'.', offerType="complaint",
                                                            offerPk=new_complaint.pk)
                    notified_user = UserProfile.objects.get(pk=admin.user)
                    notified_user.unreadcount = notified_user.unreadcount + 1
                    notified_user.save()
                messages.success(request, 'Complaint is successful.')
            return redirect('profile', pk=pk)
        else:
            return redirect('index')


class ComplaintUserEdit(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            complaint = UserComplaints.objects.get(pk=pk)
            form = ComplaintForm(instance=complaint)
            context = {
                'form': form,
                'complaint': complaint,
            }
            return render(request, 'social/complaint-edit.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
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
                        request.user) + ' edited complaint about ' + str(complaint.complainted)+'.', offerType="complaint",
                                                            offerPk=complaint.pk)
                    notified_user = UserProfile.objects.get(pk=admin.user)
                    notified_user.unreadcount = notified_user.unreadcount + 1
                    notified_user.save()
            context = {
                'form': form,
            }
            return redirect('complaintuser', pk=complaint.complainted.pk)
        else:
            return redirect('index')


class ComplaintUserDelete(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            complaint = UserComplaints.objects.get(pk=pk)
            form = ComplaintForm(instance=complaint)
            context = {
                'form': form,
            }
            return render(request, 'social/complaint-delete.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            complaint = UserComplaints.objects.get(pk=pk)
            complaint.isDeleted = True
            complaint.save()
            log = Log.objects.create(operation="deletecomplaint", itemType="user", itemId=complaint.complainted.pk,
                                    userId=request.user)

            notificationsToRead = NotifyUser.objects.filter(offerType="complaint").filter(offerPk=complaint.pk)
            for notification in notificationsToRead:
                notification.hasRead = True
                notification.save()
                userNotified = UserProfile.objects.get(pk=notification.notify)
                userNotified.unreadcount = userNotified.unreadcount - 1
                userNotified.save()

            allAdmins = UserProfile.objects.filter(isAdmin=True)
            for admin in allAdmins:
                notification = NotifyUser.objects.create(notify=admin.user,
                                                        notification=str(request.user) + ' deleted complaint about ' + str(
                                                            complaint.complainted)+'.', offerType="user",
                                                        offerPk=complaint.complainted.pk)
                notified_user = UserProfile.objects.get(pk=admin.user)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
            return redirect('profile', pk=complaint.complainted.pk)
        else:
            return redirect('index')


class Complaints(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            complaints = UserComplaints.objects.all().order_by('-date')
            complaints_count = len(complaints)
            context = {
                'complaints_count': complaints_count,
                'complaints': complaints,
            }
            return render(request, 'social/complaints.html', context)
        else:
            return redirect('index')


class ComplaintUserAdminSide(LoginRequiredMixin, View):
    def get(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            form = ComplaintFormAdmin()
            record = UserComplaints.objects.get(pk=pk)
            isSolved = record.isSolved
            context = {
                'form': form,
                'record': record,
                'isSolved': isSolved,
            }
            return render(request, 'social/complaintAdminSide.html', context)
        else:
            return redirect('index')

    def post(self, request, *args, pk, **kwargs):
        if request.user.profile.isActive:
            form = ComplaintFormAdmin(request.POST)
            complaint = UserComplaints.objects.get(pk=pk)
            if form.is_valid():
                edit_complaint = form.save(commit=False)
                complaint.solutionAction = edit_complaint.solutionAction
                complaint.solutionText = edit_complaint.solutionText
                complaint.adminDate = timezone.now()
                complaint.isSolved = True
                complaint.solutionAdmin = request.user
                complaint.save()
                log = Log.objects.create(operation="solvecomplaint", itemType="user", itemId=complaint.complainted.pk,
                                        userId=request.user)

                notificationsToRead = NotifyUser.objects.filter(offerType="complaint").filter(offerPk=complaint.pk)
                for notification in notificationsToRead:
                    notification.hasRead = True
                    notification.save()
                    userNotified = UserProfile.objects.get(pk=notification.notify)
                    userNotified.unreadcount = userNotified.unreadcount - 1
                    userNotified.save()

                notification = NotifyUser.objects.create(notify=complaint.complainter, notification=str(request.user) + ' solved your complaint about ' + str(complaint.complainted)+'.', offerType="user", offerPk=complaint.complainted.pk)
                notified_user = UserProfile.objects.get(pk=complaint.complainter)
                notified_user.unreadcount = notified_user.unreadcount + 1
                notified_user.save()
            context = {
                'form': form,
            }
            return redirect('complaintsolve', pk=complaint.pk)
        else:
            return redirect('index')


class MyComplaints(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            complaints = UserComplaints.objects.filter(complainter=request.user).filter(isDeleted=False)
            complaints_count = len(complaints)
            context = {
                'complaints_count': complaints_count,
                'complaints': complaints,
            }
            return render(request, 'social/mycomplaints.html', context)
        else:
            return redirect('index')


class ComplaintsCreatedAbout(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            pk = self.kwargs['pk']
            complaints = UserComplaints.objects.filter(complainted=pk).order_by('-date')
            complaints_count = len(complaints)
            context = {
                'complaints_count': complaints_count,
                'complaints': complaints,
            }
            return render(request, 'social/complaintsCreatedAbout.html', context)
        else:
            return redirect('index')


class ComplaintsCreator(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            pk = self.kwargs['pk']
            complaints = UserComplaints.objects.filter(complainter=pk).order_by('-date')
            complaints_count = len(complaints)
            context = {
                'complaints_count': complaints_count,
                'complaints': complaints,
            }
            return render(request, 'social/complaintsCreator.html', context)
        else:
            return redirect('index')


class ComplaintsDoneByMe(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            pk = self.kwargs['pk']
            complaints = UserComplaints.objects.filter(complainted=pk).filter(complainter=request.user).filter(isDeleted=False).order_by('-date')
            complaints_count = len(complaints)
            context = {
                'complaints_count': complaints_count,
                'complaints': complaints,
            }
            return render(request, 'social/complaintsCreator.html', context)
        else:
            return redirect('index')


class DeactivateService(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
                                                        service.name)+'.', offerType="service", offerPk=0)
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
        else:
            return redirect('index')


class DeactivateEvent(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            event = Event.objects.get(pk=pk)
            event.isActive = False
            event.save()
            notificationsToChange = NotifyUser.objects.filter(hasRead=False).filter(offerType="event").filter(offerPk=pk)
            for notificationChange in notificationsToChange:
                notificationChange.offerPk = 0
                notificationChange.save()
            notification = NotifyUser.objects.create(notify=event.eventcreater,
                                                    notification=str(request.user) + ' deactivated your event ' + str(
                                                        event.eventname)+'.', offerType="event", offerPk=0)
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
        else:
            return redirect('index')


class DeactivateUser(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
                        request.user) + ' deactivated your service ' + str(service.name)+'.', offerType="service", offerPk=0)
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
                        request.user) + ' deactivated your event ' + str(event.eventname)+'.', offerType="event", offerPk=0)
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
        else:
            return redirect('index')


class ActivateUser(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            profile = UserProfile.objects.get(pk=pk)
            profile.isActive = True
            profile.save()
            log = Log.objects.create(operation="activate", itemType="user", itemId=pk, userId=request.user)
            notification = NotifyUser.objects.create(notify=profile.user,
                                                    notification=str(request.user) + ' activated your profile.',
                                                    offerType="user", offerPk=0)
            profile.unreadcount = profile.unreadcount + 1
            profile.save()
            return redirect('profile', pk=pk)
        else:
            return redirect('index')


class DeactivateServiceApplication(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class DeactivateEventApplication(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class Deactivateds(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
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
        else:
            return redirect('index')


class FeaturedServicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            featureds = Featured.objects.filter(itemType="service").order_by('-date')
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
                'featureds': featureds
            }
            return render(request, 'social/featuredservices.html', context)
        else:
            return redirect('index')


class FeaturedEventsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.isActive:
            featureds = Featured.objects.filter(itemType="event").order_by('-date')
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
                'featureds': featureds
            }
            return render(request, 'social/featuredevents.html', context)
        else:
            return redirect('index')


class AddServiceFeatured(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            dateDiff = (datetime.now() - timedelta(days=1)).date()
            featureds = []
            featuredsToAdd = Featured.objects.filter(itemType="service").filter(date__gte=dateDiff)
            for featuredToAdd in featuredsToAdd:
                serviceFound = Service.objects.get(pk=featuredToAdd.itemId)
                if serviceFound.isActive == True and serviceFound.isDeleted == False:
                    featureds.append(featuredToAdd)
            if len(featureds) < 2:
                featured = Featured.objects.create(itemType="service", itemId=pk)

                theService = Service.objects.get(pk=pk)
                notification = NotifyUser.objects.create(notify=theService.creater, notification=str(
                    request.user) + ' added your service to featured list.', offerType="service", offerPk=pk)
                theService.creater.profile.unreadcount = theService.creater.profile.unreadcount + 1
                theService.creater.profile.save()

            else:
                messages.warning(request,
                                'You have already 2 featured services for today, please remove one to add new.')
            return redirect('service-detail', pk=pk)
        else:
            return redirect('index')


class RemoveServiceFeatured(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            featured = Featured.objects.get(itemType="service", itemId=pk)
            featured.delete()
            theService = Service.objects.get(pk=pk)
            notification = NotifyUser.objects.create(notify=theService.creater, notification=str(
                request.user) + ' removed your service from featured list.', offerType="service", offerPk=pk)
            theService.creater.profile.unreadcount = theService.creater.profile.unreadcount + 1
            theService.creater.profile.save()
            return redirect('service-detail', pk=pk)
        else:
            return redirect('index')


class AddEventFeatured(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            dateDiff = (datetime.now() - timedelta(days=1)).date()
            featureds = []
            featuredsToAdd = Featured.objects.filter(itemType="event").filter(date__gte=dateDiff)
            for featuredToAdd in featuredsToAdd:
                eventFound = Event.objects.get(pk=featuredToAdd.itemId)
                if eventFound.isActive == True and eventFound.isDeleted == False:
                    featureds.append(featuredToAdd)
            if len(featureds) < 2:
                featured = Featured.objects.create(itemType="event", itemId=pk)

                theEvent = Event.objects.get(pk=pk)
                notification = NotifyUser.objects.create(notify=theEvent.eventcreater, notification=str(
                    request.user) + ' added your event to featured list.', offerType="event", offerPk=pk)
                theEvent.eventcreater.profile.unreadcount = theEvent.eventcreater.profile.unreadcount + 1
                theEvent.eventcreater.profile.save()

            else:
                messages.warning(request, 'You have already 2 featured events for today, please remove one to add new.')
            return redirect('event-detail', pk=pk)
        else:
            return redirect('index')


class RemoveEventFeatured(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.profile.isActive:
            featured = Featured.objects.get(itemType="event", itemId=pk)
            featured.delete()
            theEvent = Event.objects.get(pk=pk)
            notification = NotifyUser.objects.create(notify=theEvent.eventcreater, notification=str(
                request.user) + ' removed your event from featured list.', offerType="event", offerPk=pk)
            theEvent.eventcreater.profile.unreadcount = theEvent.eventcreater.profile.unreadcount + 1
            theEvent.eventcreater.profile.save()
            return redirect('event-detail', pk=pk)
        else:
            return redirect('index')


class RecommendationsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        own_recommendations = get_recommendations(request)
        context = {
            "recommendations":own_recommendations,
            "recommendations_count": len(own_recommendations)
        }
        return render(request, 'social/recommendations.html', context)

class RecommendationApproveView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        wiki = Service.objects.get(pk=pk).wiki_description.split("as a(n) ")[1]
        Interest.objects.filter(user=request.user).filter(wiki_description=wiki).update(feedbackGiven=True, feedbackFactor = F('feedbackFactor') + 1)
        own_recommendations = get_recommendations(request)
        context = {
            "recommendations":own_recommendations,
            "recommendations_count": len(own_recommendations)
        }
        return render(request, 'social/recommendations.html', context)

class RecommendationDisapproveView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        wiki = Service.objects.get(pk=pk).wiki_description.split("as a(n) ")[1]
        Interest.objects.filter(user=request.user).filter(wiki_description=wiki).update(feedbackGiven=True, feedbackFactor=F('feedbackFactor') - 1)
        interest = Interest.objects.filter(user=request.user).filter(wiki_description=wiki)
        if len(interest)>0:
            interest[0].disapprovedServices.add(Service.objects.get(pk=pk))
        own_recommendations = get_recommendations(request)
        context = {
            "recommendations":own_recommendations,
            "recommendations_count": len(own_recommendations)
        }
        return render(request, 'social/recommendations.html', context)

def get_recommendations(request):

    def sub_date_picked(search_results):
        def sub_date_sorted(service):
            return service.creater.date_joined

        services_sub_date_sorted = sorted(search_results, reverse=True, key=sub_date_sorted)
        return services_sub_date_sorted[0]

    def rating_picked(search_results):
        ratings = []

        def rating_sorted(service):
            past_ratings = UserRatings.objects.filter(service=service)
            ratings_average = UserRatings.objects.filter(rated=service.creater).aggregate(Avg('rating'))['rating__avg']
            return ratings_average if (len(past_ratings) != 0) else 0

        for service in search_results:
            ratings.append(rating_sorted(service))

        services_rating_sorted = sorted(search_results, reverse=True, key=rating_sorted)

        num_of_services = ratings.count(ratings[0])
        if num_of_services > 1:
            return services_rating_sorted[randrange(num_of_services)]
        else:
            return services_rating_sorted[0]

    def smart_sort(services):
        random_pick = randrange(2)
        if random_pick == 0:
            service = sub_date_picked(services)
            return service
        elif random_pick == 1:
            service = rating_picked(services)
            return service

    def sort_interests(interests):
        desc = []
        for interest in interests:
            desc.append(interest.wiki_description)
        currentTime = timezone.now()
        all_services_sorted = []

        if len(desc) == 0:
            return all_services_sorted
        else:
            all_services = list(Service.objects.exclude(wiki_description__isnull=True).filter(
                reduce(operator.or_, (Q(wiki_description__contains=x) for x in desc))).exclude(creater=request.user).filter(isDeleted=False).filter(isActive=True).filter(servicedate__gte=currentTime))

        while len(all_services) > len(all_services_sorted):
            for interest in interests:
                current_interest_list = list(
                    filter(lambda it: interest.wiki_description in it.wiki_description and it not in interest.disapprovedServices.all(), all_services))
                if len(current_interest_list) > interest.feedbackFactor:
                    for i in range(interest.feedbackFactor):
                        selected_service = smart_sort(current_interest_list)
                        all_services_sorted.append(selected_service)
                        all_services.remove(selected_service)
                elif len(current_interest_list) > 0:
                    for service in current_interest_list:
                        all_services_sorted.append(service)
                    for service in current_interest_list:
                        all_services.remove(service)
                else:
                    pass
        return all_services_sorted

    own_recommendations = sort_interests(Interest.objects.filter(user=request.user).order_by('feedbackFactor'))
    if User.objects.get(pk=request.user.pk).date_joined > timezone.now() - timedelta(days=30):
        followed_list = []
        profiles = UserProfile.objects.filter(followers__id__exact=request.user.id)
        if len(profiles) == 0:
            return own_recommendations
        else:
            for followed in profiles:
                followed_list.append(followed.user)
            followed_interests = Interest.objects.exclude(user=request.user).filter(
                reduce(operator.or_, (Q(user=followed) for followed in followed_list)))
            if len(followed_interests) > 0:
                for service in sort_interests(followed_interests):
                    own_recommendations.append(service)
    return own_recommendations

def find_location(request):

    form = MyLocation(request.GET)
    search=request.session.get("search")


    if 'submit' in request.GET:
        if form.is_valid():
            target_location = form.cleaned_data.get("location")
            request.session["target_location"]=target_location
            distance=request.GET.get("distance")
            request.session["distance"] = distance

    context={
        "form":form,
        "search":search,
    }
    return render(request, "social/map.html", context)