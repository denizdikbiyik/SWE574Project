from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic

from django.contrib.auth.models import AbstractUser, User

from social.models import UserProfile
from django.core.paginator import Paginator
import datetime

from .forms import PeriodPicker


# helper function to get context from the form
def make_context_for_username_list(*args):
    date_today = datetime.datetime.now()
    is_pick_date = False

    users = User.objects.all()

    context = {}
    if args[0] == "week":
        time_delta = 7
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        users = users.filter(date_joined__gte=date_old, date_joined__lte=date_today)

        context["text"] = "Showing the usernames created in the last 7 days."
    elif args[0] == "month":
        time_delta = 30
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        users = users.filter(date_joined__gte=date_old, date_joined__lte=date_today)

        context["text"] = "Showing the users created in the last 30 days."
    elif args[0] == "all":
        users = users
        context["text"] = "Showing all the users created."
    else:
        is_pick_date = True
        date_old = args[1]
        date_new = args[2]
        if date_new != None and date_old != None:
            users = users.filter(date_joined__gte=date_old, date_joined__lte=date_new)

            context["text"] = "Showing the users created between the selected dates."
    context["is_pick_date"] = is_pick_date
    user_count = users.count()
    if user_count == 0:
        context["text"] = ""
    context["users"] = users
    context["user_count"] = user_count
    return context


def list_users(request):
    if request.method == 'POST':
        applications = User.objects.all()

        form = PeriodPicker(request.POST)
        if form.is_valid():
            form_field1 = form.cleaned_data.get("period")
            form_field2 = form.cleaned_data.get("date_old")
            form_field3 = form.cleaned_data.get("date_new")
            #form_field4 = form.cleaned_data.get("sort")
            context = make_context_for_username_list(form_field1, form_field2, form_field3)
            context["form"] = form
            context["applications"] = applications
            context["applicationslength"] = len(applications)
            return render(request, 'dashboard_user_list/userlist.html', context)
    else:
        form = PeriodPicker()
    return render(request, 'dashboard_user_list/userlist.html', {'form': form})

