from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic

from social.models import Service, ServiceApplication
from django.core.paginator import Paginator
import datetime

from .forms import PeriodPicker


# helper function to get context from the form
def make_context_for_service_list(*args):
    date_today = datetime.datetime.now()
    is_pick_date = False
    order_by = args[3]
    services = Service.objects.all().order_by(
        order_by)
    context = {}
    if args[0] == "week":
        time_delta = 7
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        services = services.filter(createddate__gte=date_old, createddate__lte=date_today).order_by(
            order_by)
        context["text"] = "Showing the services created in the last 7 days."
    elif args[0] == "month":
        time_delta = 30
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        services = services.filter(createddate__gte=date_old, createddate__lte=date_today).order_by(
            order_by)
        context["text"] = "Showing the services created in the last 30 days."
    elif args[0] == "all":
        services = services
        context["text"] = "Showing all the services created."
    else:
        is_pick_date = True
        date_old = args[1]
        date_new = args[2]
        if date_new != None and date_old != None:
            services = services.filter(createddate__gte=date_old, createddate__lte=date_new).order_by(
                order_by)
            context["text"] = "Showing the services created between the selected dates."
    context["is_pick_date"] = is_pick_date
    service_count = services.count()
    if service_count == 0:
        context["text"] = ""
    context["services"] = services
    context["service_count"] = service_count
    return context


def list_services(request):
    if request.method == 'POST':
        applications = ServiceApplication.objects.all()
        form = PeriodPicker(request.POST)
        if form.is_valid():
            form_field1 = form.cleaned_data.get("period")
            form_field2 = form.cleaned_data.get("date_old")
            form_field3 = form.cleaned_data.get("date_new")
            form_field4 = form.cleaned_data.get("sort")
            context = make_context_for_service_list(form_field1, form_field2, form_field3, form_field4)
            context["form"] = form
            context["applications"] = applications
            context["applicationslength"] = len(applications)
            return render(request, 'dasboard_service_list/servicelist.html', context)
    else:
        if request.user.profile.isAdmin:
            form = PeriodPicker()
        else:
            return redirect('index')
    return render(request, 'dasboard_service_list/servicelist.html', {'form': form})
