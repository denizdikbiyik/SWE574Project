from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from social.models import Event
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime
import re


def make_query_for_event_list(*args):
    date_today = datetime.datetime.now()
    context = {}
    if args[0] == "week":
        time_delta = 7
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        date_new = date_today
        context["text"] = "Period: Last 7 days"
    elif args[0] == "month":
        time_delta = 30
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        date_new = date_today
        context["text"] = "Period: Last 30 days."
    elif args[0] == "year":
        time_delta = 365
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        date_new = date_today
        context["text"] = "Period: Last 365 days."
    else:
        date_old = args[1]
        date_new = args[2]
        context["text"] = "Period: Between the selected dates."
    context["date_old"] = date_old
    context["date_new"] = date_new
    return context


def list_events(request):
    if request.user.profile.isAdmin:
        is_admin = True
        type = request.GET.get("type")
        periods = request.GET.get("periods")
        beginning = request.GET.get("beginning")
        ending = request.GET.get("ending")
        status = request.GET.get("status")
        q = request.GET.get("q")
        # qlocation = request.GET.get("qlocation")
        sort = request.GET.get("sort")
        # submit = request.GET.get("submitted")
        events = Event.objects.all()
        status_message = ""
        period_message = ""
        date_today = datetime.datetime.now()
        outdated_events = Event.objects.all().filter(eventdate__lte=date_today)
        period = make_query_for_event_list(periods, beginning, ending)
        show_count = False

        if 'submit' in request.GET and ((beginning == "" and ending == "") or (periods == "") or (
                periods == None and beginning == None and ending == None)):
            period_message = "Please choose a period!"
            show_count = show_count
        if (periods == None and beginning == None and ending == None) or (
                periods == None and beginning == "" and ending == "") or (
                period["date_old"] == "" and period["date_new"] == "") or (periods == ""):
            events = Event.objects.none()
            show_count = show_count
        else:
            if periods == "all":
                events = events
                # period_message = "Period: All times"
                show_count = True
            elif (beginning != "" and ending == "") or (beginning == "" and ending != ""):
                events = Event.objects.none()
                period_message = "You must choose two dates!"
            elif periods == None and (period["date_old"] > period["date_new"]):
                events = Event.objects.none()
                period_message = "Beginning date can't be older than ending date!"
            else:
                events = events.filter(eventcreateddate__gte=period["date_old"],
                                       eventcreateddate__lte=period["date_new"])
                # period_message = period["text"]
                show_count = True

        if status == "all":
            events = events
            status_message = "Status: All"
        elif status == "isDeleted":
            events = events.filter(isDeleted=True)
            status_message = "Status: Deleted"
        elif status == "isActive":
            events = events.filter(isActive=False)
            status_message = "Status: Inactive"
        else:
            events = events
            status_message = status_message

        if q == None or q == "":
            events = events
        else:
            events_pk = set()
            for event in events:
                address = event.event_address
                if re.search(q, address, re.IGNORECASE):
                    events_pk.add(event.pk)
            events = events.filter(
                Q(eventname__icontains=q) | Q(eventdescription__icontains=q) | Q(
                    event_wiki_description__icontains=q) | Q(
                    event_address__icontains=q) | Q(pk__in=events_pk))

        '''
        if qlocation == None or qlocation == "":
            events = events
        else:
            events = events.filter(
                Q(event_address__icontains=qlocation))
        '''

        if sort == "name":
            events = events.order_by("eventname")
        elif sort == "createddate":
            events = events.order_by("eventcreateddate")
        else:
            events = events.order_by("eventdate")

        if 'submit' in request.GET:
            if periods != None or periods != None:
                type = "default"
            elif (beginning != None or beginning != None) or (ending != None or ending != None):
                type = "pick"
            else:
                type = None

        event_count = events.count()
        object_list = events
        page_num = request.GET.get('page', 1)
        paginator = Paginator(object_list, 5)
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)
        return render(request, 'dashboard_event_list/eventlist.html',
                      {'page_obj': page_obj, "type": type, "periods": periods, "beginning": beginning, "ending": ending,
                       "status": status, "q": q, "sort": sort, "event_count": event_count,
                       "is_admin": is_admin, "status_message": status_message, "period_message": period_message,
                       "outdated_events": outdated_events, "show_count": show_count})

    else:
        return redirect('index')
