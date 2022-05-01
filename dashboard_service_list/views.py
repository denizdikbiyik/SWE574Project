from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from social.models import Service
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime
import re


def make_query_for_service_list(*args):
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


def list_services(request):
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
        services = Service.objects.all()
        status_message = ""
        period_message = ""
        date_today = datetime.datetime.now()
        outdated_services = Service.objects.all().filter(servicedate__lte=date_today)
        period = make_query_for_service_list(periods, beginning, ending)
        show_count = False

        if 'submit' in request.GET and ((beginning == "" and ending == "") or (periods == "") or (
                periods == None and beginning == None and ending == None)):
            period_message = "Please choose a period!"
            show_count = show_count
        if (periods == None and beginning == None and ending == None) or (
                periods == None and beginning == "" and ending == "") or (
                period["date_old"] == "" and period["date_new"] == "") or (periods == ""):
            services = Service.objects.none()
            show_count = show_count
        else:
            if periods == "all":
                services = services
                # period_message = "Period: All times"
                show_count = True
            elif (beginning != "" and ending == "") or (beginning == "" and ending != ""):
                services = Service.objects.none()
                period_message = "You must choose two dates!"
            elif periods == None and (period["date_old"] > period["date_new"]):
                services = Service.objects.none()
                period_message = "Beginning date can't be older than ending date!"
            else:
                services = services.filter(createddate__gte=period["date_old"],
                                           createddate__lte=period["date_new"])
                # period_message = period["text"]
                show_count = True

        if status == "all":
            services = services
            status_message = "Status: All"
        elif status == "handshake":
            services = services.filter(is_taken=True, is_given=True)
            status_message = "Status: Handshake"
        elif status == "isDeleted":
            services = services.filter(isDeleted=True)
            status_message = "Status: Deleted"
        elif status == "isActive":
            services = services.filter(isActive=False)
            status_message = "Status: Inactive"
        else:
            services = services
            status_message = status_message

        if q == None or q == "":
            services = services
        else:
            services_pk = set()
            for service in services:
                address = service.address
                if re.search(q, address, re.IGNORECASE):
                    services_pk.add(service.pk)
            services = services.filter(
                Q(name__icontains=q) | Q(description__icontains=q) | Q(wiki_description__icontains=q) | Q(
                    address__icontains=q) | Q(pk__in=services_pk))

        '''
        if qlocation == None or qlocation == "":
            services = services
        else:
            services = services.filter(
                Q(address__icontains=qlocation))
        '''

        if sort == "name":
            services = services.order_by("name")
        elif sort == "createddate":
            services = services.order_by("createddate")
        else:
            services = services.order_by("servicedate")

        if 'submit' in request.GET:
            if periods != None or periods != None:
                type = "default"
            elif (beginning != None or beginning != None) or (ending != None or ending != None):
                type = "pick"
            else:
                type = None

        service_count = services.count()
        object_list = services
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
        return render(request, 'dasboard_service_list/servicelist.html',
                      {'page_obj': page_obj, "type": type, "periods": periods, "beginning": beginning, "ending": ending,
                       "status": status, "q": q, "sort": sort, "service_count": service_count,
                       "is_admin": is_admin, "status_message": status_message, "period_message": period_message,
                       "outdated_services": outdated_services, "show_count": show_count})

    else:
        return redirect('index')
