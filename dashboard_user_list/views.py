from django.contrib.auth.models import AbstractUser, User
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.shortcuts import render, get_object_or_404, redirect
from psutil import users
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime



def make_query_for_users_list(*args):
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


def list_users(request):
    if request.user.profile.isActive:
        if request.user.profile.isAdmin:
            is_admin = True
            type = request.GET.get("type")
            periods = request.GET.get("periods")
            beginning = request.GET.get("beginning")
            ending = request.GET.get("ending")
            q = request.GET.get("q")
            #submit = request.GET.get("submitted")
            users= User.objects.all()
            period_message = ""
            date_today = datetime.datetime.now()
            period = make_query_for_users_list(periods, beginning, ending)
            show_count = False

            if 'submit' in request.GET and ((beginning == "" and ending == "") or (periods == "") or (
                    periods == None and beginning == None and ending == None)):
                period_message = "Please choose a period!"
                show_count = show_count

            if (periods == None and beginning == None and ending == None) or (
                    periods == None and beginning == "" and ending == "") or (
                    period["date_old"] == "" and period["date_new"] == "") or (periods == ""):
                users= User.objects.none()
                show_count = show_count
            else:
                if periods == "all":
                    users = users
                    period_message = "Period: All times"
                    show_count = True
                elif (beginning != "" and ending == "") or (beginning == "" and ending != ""):
                    users = User.objects.none()
                    period_message = "You must choose two dates!"
                elif periods == None and (period["date_old"] > period["date_new"]):
                    users = User.objects.none()
                    period_message = "Beginning date can't be older than ending date!"
                else:
                    users= users.filter(date_joined__gte=period["date_old"],
                                        date_joined__lte=period["date_new"])
                    period_message = period["text"]
                    show_count = True

            if q == None or q == "":
                users = users
            else:
                users = users.filter(
                    Q(username__icontains=q) | Q(username__icontains=q))


            if 'submit' in request.GET:
                if periods != None or periods != None:
                    type = "default"
                elif (beginning != None or beginning != None) or (ending != None or ending != None):
                    type = "pick"
                else:
                    type = None
                
            user_count = users.count()
            object_list = users
            page_num = request.GET.get('page', 1)
            paginator = Paginator(object_list, 10)  # 10 employees per page
            try:
                page_obj = paginator.page(page_num)
            except PageNotAnInteger:
                # if page is not an integer, deliver the first page
                page_obj = paginator.page(1)
            except EmptyPage:
                # if the page is out of range, deliver the last page
                page_obj = paginator.page(paginator.num_pages)
            return render(request, 'dashboard_user_list/userlist.html',
                        {'page_obj': page_obj, "type": type, "periods": periods, "beginning": beginning, "ending": ending,
                            "user_count": user_count, "q": q,
                        "is_admin": is_admin,  "period_message": period_message,
                        "show_count": show_count})
        else:
            return redirect('index')
    else:
        return redirect('index')
