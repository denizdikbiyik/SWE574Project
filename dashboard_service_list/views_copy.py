from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from social.models import Service, ServiceApplication
import datetime

from .forms import PeriodPicker

'''
def list_services(request):
    if request.method == 'POST':
        form = PeriodPicker(request.POST)
        services = Service.objects.all()
        service_count = services.count()
        applications = ServiceApplication.objects.all()
        date_today = datetime.datetime.now()
        is_pick_date = False
        main_title_input = ""
        sub_title_input = ""
        if form.is_valid():
            if form.cleaned_data.get("period") == "week":
                time_delta = 7
                date_old = (date_today - datetime.timedelta(days=time_delta)).date()
                services = services.filter(createddate__gte=date_old, createddate__lte=date_today).order_by(
                    "createddate")
                service_count = services.count()
                main_title_input = "Showing services created in the last 7 days."
            elif form.cleaned_data.get("period") == "month":
                time_delta = 30
                date_old = (date_today - datetime.timedelta(days=time_delta)).date()
                services = services.filter(createddate__gte=date_old, createddate__lte=date_today).order_by(
                    "createddate")
                service_count = services.count()
                main_title_input = "Showing services created in the last 30 days."
            elif form.cleaned_data.get("period") == "all":
                services = services
                main_title_input = "Showing all the services created."
            else:
                is_pick_date = True
                date_new = form.cleaned_data.get("date_new")
                date_old = form.cleaned_data.get("date_old")
                if date_new != None and date_old != None:
                    services = services.filter(createddate__gte=date_old, createddate__lte=date_new).order_by(
                        "createddate")
                    service_count = services.count()
                    main_title_input = "Showing all the services created between the chosen dates."
            if service_count == 0:
                sub_title_input = "Sorry, no matches found!"
            elif service_count == 1:
                sub_title_input = "We have found 1 match."
            else:
                sub_title_input = f"We have found {service_count} matches."
            return render(request, 'dasboard_list/servicelist.html',
                          {'form': form, "services": services, "service_count": service_count,
                           "applications": applications, "is_pick_date": is_pick_date,
                           "main_title_input": main_title_input, "sub_title_input": sub_title_input})
    else:
        form = PeriodPicker()
    return render(request, 'dasboard_list/servicelist.html', {'form': form})
'''

'''
def list_services(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # add the dictionary during initialization
    context["dataset"] = Service.objects.all()

    return render(request, 'dasboard_list/list.html', context)
'''


def make_context_new(form):
    services = Service.objects.all()
    date_today = datetime.datetime.now()
    if form.cleaned_data.get("period") == "week":
        time_delta = 7
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        services = services.filter(createddate__gte=date_old, createddate__lte=date_today).order_by(
            "createddate")
    elif form.cleaned_data.get("period") == "month":
        time_delta = 30
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        services = services.filter(createddate__gte=date_old, createddate__lte=date_today).order_by(
            "createddate")
    elif form.cleaned_data.get("period") == "all":
        services = services
    else:
        date_old = form.cleaned_data.get("date_old")
        date_new = form.cleaned_data.get("date_new")
        if date_new != None and date_old != None:
            services = services.filter(createddate__gte=date_old, createddate__lte=date_new).order_by(
                "createddate")
    return services


def form_view_new(request):
    if request.method == 'POST':
        form = PeriodPicker(request.POST)
        is_pick_date = False
        if form.is_valid():
            if form.cleaned_data.get("period") == "select":
                is_pick_date = True
            services = make_context_new(form)
            return redirect("servicelist", services)
    else:
        form = PeriodPicker()
    return render(request, 'dasboard_list/dashboard.html', {'form': form})


def list_services(request, services):
    # dictionary for initial data with
    # field names as keys
    context = {}
    # add the dictionary during initialization
    context["applications"] = ServiceApplication.objects.all()
    context["services"] = services
    return render(request, 'dasboard_list/servicelist.html', context)


'''
def form_view(request):
    if request.method == 'POST':
        form = PeriodPicker(request.POST)
        form_output = []
        is_pick_date = False
        if form.is_valid():
            form_output_period = form.cleaned_data.get("period")
            form_output.append(form_output_period)
            if form_output_period == "select":
                is_pick_date = True
                form_output_date_old = form.cleaned_data.get("date_old")
                form_output.append(form_output_date_old)
                form_output_date_new = form.cleaned_data.get("date_new")
                form_output.append(form_output_date_new)
                return render(request, 'dasboard_list/dashboard.html', {'form': form, "is_pick_date": is_pick_date}, form_output)
    else:
        form = PeriodPicker()
    return render(request, 'dasboard_list/dashboard.html', {'form': form})
'''

'''
def make_context(form_output):
    services = Service.objects.all()
    date_today = datetime.datetime.now()
    if form_output[0] == "week":
        time_delta = 7
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        services = services.filter(createddate__gte=date_old, createddate__lte=date_today).order_by(
            "createddate")
    elif form_output[0] == "month":
        time_delta = 30
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        services = services.filter(createddate__gte=date_old, createddate__lte=date_today).order_by(
            "createddate")
    elif form_output[0] == "all":
        services = services
    else:
        date_old = form_output[1]
        date_new = form_output[2]
        if date_new != None and date_old != None:
            services = services.filter(createddate__gte=date_old, createddate__lte=date_new).order_by(
                "createddate")
    return services
'''
