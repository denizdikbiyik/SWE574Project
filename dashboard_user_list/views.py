from genericpath import exists
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic

from django.contrib.auth.models import AbstractUser, User

from social.models import UserProfile
from django.core.paginator import Paginator
import datetime

from .forms import PeriodPickerUser


# helper function to get context from the form
def make_context_for_username_list(*args):
    date_today = datetime.datetime.now()
    is_pick_date = False
    users = User.objects.all()

    context = {}
    if args[0] == "week":
        time_delta = 7
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        users = users.filter(date_joined__gte=date_old , date_joined__lte=date_today)
        context["text"] = "Showing the usernames created in the last 7 days."
        date_new = datetime.date.today()
    elif args[0] == "month":
        time_delta = 30
        date_old = (date_today - datetime.timedelta(days=time_delta)).date()
        users = users.filter(date_joined__gte=date_old, date_joined__lte=date_today)
        date_new = datetime.date.today()

        context["text"] = "Showing the users created in the last 30 days."
    elif args[0] == "all":
        users = users
        context["text"] = "Showing all the users created."
        # in case no user exists, give random date_new and date_old 
        date_new = datetime.date.today()
        date_old = datetime.date(2000, 1, 1)

    else:
        is_pick_date = True
        date_old = args[1]
        date_new = args[2]
        
        if date_old == None and date_new == None:
            users = users
            date_old = datetime.date(2000, 1, 1)
            date_new = datetime.date.today()
            context["text"] = "Please Select at Least One Date."

        elif date_old != None and date_new == None:
            date_new = datetime.date.today()
            users = users.filter(date_joined__gte=date_old, date_joined__lte=date_new)
            context["text"] = "Showing the users created after selected beginning date."

        elif date_old == None and date_new != None:
            date_old = datetime.date(2000, 1, 1)
            users = users.filter(date_joined__gte=date_old, date_joined__lte=date_new)
            context["text"] = "Showing the users created before selected ending date."

        elif date_new != None and date_old != None:    
            users = users.filter(date_joined__gte=date_old, date_joined__lte=date_new)
            context["text"] = "Showing the users created between the selected dates."
    
    context["is_pick_date"] = is_pick_date
    user_count = users.count()
    
    if user_count == 0:
        if date_old > date_new:# and is_pick_date == False:
            context["text"] = "End date should be greater than start date."
        else:
            context["text"] = ""
    else: 
        if date_old > date_new:# and is_pick_date == False:
            context["text"] = "End date should be greater than start date."
    
    context["users"] = users
    context["user_count"] = user_count
    return context


def list_users(request):
    if request.method == 'POST':
        applications = User.objects.all()

        form = PeriodPickerUser(request.POST)
        if form.is_valid():
            form_field1 = form.cleaned_data.get("period")
            form_field2 = form.cleaned_data.get("date_old")
            form_field3 = form.cleaned_data.get("date_new")
            #form_field4 = form.cleaned_data.get("sort")
            context = make_context_for_username_list(form_field1, form_field2, form_field3)
            context["form"] = form
            context["applications"] = applications
            context["applicationslength"] = len(applications)
            # Clears the list when "Select Dates" is selected and submitted
            if form.cleaned_data.get("period") == "select" and form.cleaned_data.get("date_old") == None and form.cleaned_data.get("date_new") == None: 
                context["users"] = None
                context["clear_list"] = True
            else:
                context["clear_list"] = False
            return render(request, 'dashboard_user_list/userlist.html', context)
    else:
        if request.user.profile.isAdmin:
            form = PeriodPickerUser()
        else:
            return redirect('index')
    return render(request, 'dashboard_user_list/userlist.html', {'form': form})
     

