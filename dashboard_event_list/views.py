from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic

from social.models import Service, ServiceApplication, Event, EventApplication
from django.core.paginator import Paginator
import datetime

from .forms import PeriodPicker


def make_context_for_event_list(*args):
    date_today = datetime.datetime.now()
    is_pick_date = False
    if args[3] == "createdate":
        order_by = "eventcreateddate"
    else:
        order_by = "eventdate"
    events = Event.objects.all().order_by(
        order_by)
    context = {}
    if args[0] == "week":
        time_delta = 7
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        events = events.filter(eventcreateddate__gte=date_old, eventcreateddate__lte=date_today).order_by(
            order_by)
        context["text"] = "Showing the events created in the last 7 days."
    elif args[0] == "month":
        time_delta = 30
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        events = events.filter(eventcreateddate__gte=date_old, eventcreateddate__lte=date_today).order_by(
            order_by)
        context["text"] = "Showing the events created in the last 30 days."
    elif args[0] == "all":
        events = events
        context["text"] = "Showing all the events created."
    else:
        is_pick_date = True
        date_old = args[1]
        date_new = args[2]
        if date_new != None and date_old != None:
            events = events.filter(eventcreateddate__gte=date_old, eventcreateddate__lte=date_new).order_by(
                order_by)
            context["text"] = "Showing the events created between the selected dates."
    context["is_pick_date"] = is_pick_date
    event_count = events.count()
    if event_count == 0:
        context["text"] = ""
    context["events"] = events
    context["event_count"] = event_count
    return context


def list_events(request):
    if request.method == 'POST':
        applications = EventApplication.objects.all()
        form = PeriodPicker(request.POST)
        if form.is_valid():
            form_field1 = form.cleaned_data.get("period")
            form_field2 = form.cleaned_data.get("date_old")
            form_field3 = form.cleaned_data.get("date_new")
            form_field4 = form.cleaned_data.get("sort")
            context = make_context_for_event_list(form_field1, form_field2, form_field3, form_field4)
            context["form"] = form
            context["applications"] = applications
            # Clears the list when "Select Dates" is selected and submitted
            if form.cleaned_data.get("period") == "select" and form.cleaned_data.get("date_old") == None:
                context["events"] = None
                context["clear_list"] = True
            else:
                context["clear_list"] = False
            return render(request, 'dashboard_event_list/eventlist.html', context)
    else:
        form = PeriodPicker()
    return render(request, 'dashboard_event_list/eventlist.html', {'form': form})
