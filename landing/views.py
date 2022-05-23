from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views import View
from social.models import Service, UserProfile, Event, ServiceApplication, Featured, Interest, UserRatings
from django.contrib.auth.models import User
from social.forms import ServiceForm, EventForm, ServiceApplicationForm
from django.views.generic.edit import UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
import datetime
from online_users.models import OnlineUserActivity
from functools import reduce
import operator
from random import randrange
from django.db.models import Q, F, Avg

class Index(View):
    def get(self, request, *args, **kwargs):
        currentTime = timezone.now()
        services = []
        events = []
        featured_services = []
        featured_events = []

        dateDiff = (datetime.datetime.now() - datetime.timedelta(days=1)).date()

        featuredServicesList = Featured.objects.filter(itemType="service").filter(date__gte=dateDiff)
        for featuredServiceList in featuredServicesList:
            serviceFeatured = Service.objects.get(pk=featuredServiceList.itemId)
            if serviceFeatured.isActive == True and serviceFeatured.isDeleted == False and serviceFeatured.servicedate >= currentTime:
                featured_services.append(serviceFeatured)
        featured_services_count = len(featured_services)
        featuredEventsList = Featured.objects.filter(itemType="event").filter(date__gte=dateDiff)
        for featuredEventList in featuredEventsList:
            eventFeatured = Event.objects.get(pk=featuredEventList.itemId)
            if eventFeatured.isActive == True and eventFeatured.isDeleted == False and eventFeatured.eventdate >= currentTime:
                featured_events.append(eventFeatured)
        featured_events_count = len(featured_events)

        servicesToGet = Service.objects.filter(isDeleted=False).filter(isActive=True).filter(servicedate__gte=currentTime).order_by('-createddate')
        for serviceToGet in servicesToGet:
            if serviceToGet not in featured_services:
                services.append(serviceToGet)
        eventsToGet = Event.objects.filter(isDeleted=False).filter(isActive=True).filter(eventdate__gte=currentTime).order_by('-eventcreateddate')
        for eventToGet in eventsToGet:
            if eventToGet not in featured_events:
                events.append(eventToGet)

        context = {
            'services': services[:5],
            'events': events[:5],
            'services_count': 5,
            'events_count': 5,
            'featured_services': featured_services,
            'featured_events': featured_events,
            'featured_services_count': featured_services_count,
            'featured_events_count': featured_events_count,
            'currentTime': currentTime
        }

        if request.user.is_anonymous:
            pass
        else:
            recommendations = get_recommendations(request)
            if len(recommendations)>0:
                recommendation = recommendations[randrange(len(recommendations))]
                context['recommendation'] = recommendation

        return render(request, 'landing/index.html', context)

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
        all_services = []
        currentTime = timezone.now()
        for interest in interests:
            desc.append(interest.name + " as a(n) " + interest.wiki_description)
            current_interest_list = list(Service.objects.exclude(wiki_description__isnull=True).filter(
                reduce(operator.or_, (Q(wiki_description=x) for x in desc))).exclude(creater=request.user).filter(
                isDeleted=False).filter(isActive=True).filter(servicedate__gte=currentTime).filter(
                wiki_description=interest.name + " as a(n) " + interest.wiki_description).exclude(
                pk__in=list(interest.disapprovedServices.values_list("pk", flat=True))))
            for service in current_interest_list:
                all_services.append(service)

        all_services_sorted = []

        if len(desc) == 0:
            return all_services_sorted

        while len(all_services) > 0:
            for interest in interests:
                current_list = list(filter(
                    lambda service: service.wiki_description == interest.name + " as a(n) " + interest.wiki_description,
                    all_services))
                if len(current_list) > interest.feedbackFactor:
                    for _ in range(interest.feedbackFactor):
                        selected_service = smart_sort(current_list)
                        all_services_sorted.append(selected_service)
                        if selected_service in all_services:
                            all_services.remove(selected_service)
                elif len(current_list) > 0:
                    for service in current_list:
                        all_services_sorted.append(service)
                        all_services.remove(service)
                else:
                    pass
        return all_services_sorted

    own_recommendations = sort_interests(Interest.objects.filter(user=request.user).filter(feedbackFactor__gt=0).order_by('feedbackFactor'))
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