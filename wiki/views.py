from django.shortcuts import render, redirect
import requests
from social.models import User, Interest, Service, Event


# Check 01.05.22 15:47

def get_wiki_description(query):
    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": query
    }
    descriptions = []
    try:
        response = requests.get(API_ENDPOINT, params=params)
        json_object = response.json()
        search = json_object.get("search")
        if search == None:
            descriptions = descriptions
        else:
            for i in range(len(search)):
                print(search[i]["description"])
                descriptions.append(search[i]["description"])
    except:
        descriptions = descriptions

    return descriptions


def list_descriptions(request):
    if request.user.profile.isActive:
        q = request.GET.get("q")
        description = request.POST.get("choose_description")
        message = ""
        is_choice = False
        descriptions = []
        back_link= None
        if request.session.get("type") == "event":
            back_link="event"
        elif request.session.get("type") == "service":
            back_link = "service"

        if 'submit' in request.GET:
            if q == None or q == "":
                message = "Please enter a keyword!"
            else:
                descriptions = get_wiki_description(q)
                is_choice = True
                if len(descriptions) == 0:
                    message = "No descriptions found!"

        if "save" in request.POST:
            if description is None or description == "" or description == "Descriptions":
                request.session['description'] = None
                message = "Nothing to save!"

            else:
                request.session['description'] = q + " as a(n) " + description
                message = "Saved: " + request.session['description']

        return render(request, 'wiki/wiki_description.html',
                    {'message': message, "descriptions": descriptions, "q": q, "is_choice": is_choice,
                    "back_link": back_link})
    else:
        return redirect('index')

def edit_service_descriptions(request, pk):
    if request.user.profile.isActive:
        service=Service.objects.get(pk=pk)
        wiki_description=service.wiki_description
        if wiki_description == None:
            wiki_description="None"
        q = request.GET.get("q")
        description = request.POST.get("choose_description")
        message = ""
        is_choice = False
        descriptions = []

        if 'submit' in request.GET:
            if q == None or q == "":
                message = "Please enter a keyword!"
            else:
                descriptions = get_wiki_description(q)
                is_choice = True
                if len(descriptions) == 0:
                    message = "No descriptions found!"

        if "save" in request.POST:
            if description is None or description == "" or description == "Descriptions":
                request.session['description'] = None
                message = "Nothing to save!"

            else:
                request.session['description'] = q + " as a(n) " + description
                message = "New Description Saved: " + request.session['description']

        return render(request, 'wiki/wiki_ser_desc_edit.html',
                    {'message': message, "descriptions": descriptions, "q": q, "is_choice": is_choice,
                    "wiki_description": wiki_description, "service":service})
    else:
        return redirect('index')

def edit_event_descriptions(request, pk):
    if request.user.profile.isActive:
        event=Event.objects.get(pk=pk)
        wiki_description=event.event_wiki_description
        if wiki_description == None:
            wiki_description="None"
        q = request.GET.get("q")
        description = request.POST.get("choose_description")
        message = ""
        is_choice = False
        descriptions = []

        if 'submit' in request.GET:
            if q == None or q == "":
                message = "Please enter a keyword!"
            else:
                descriptions = get_wiki_description(q)
                is_choice = True
                if len(descriptions) == 0:
                    message = "No descriptions found!"

        if "save" in request.POST:
            if description is None or description == "" or description == "Descriptions":
                request.session['description'] = None
                message = "Nothing to save!"

            else:
                request.session['description'] = q + " as a(n) " + description
                message = "New Description Saved: " + request.session['description']

        return render(request, 'wiki/wiki_event_desc_edit.html',
                    {'message': message, "descriptions": descriptions, "q": q, "is_choice": is_choice,
                    "wiki_description": wiki_description, "event":event})
    else:
        return redirect('index')

def list_interests(request):
    if request.user.profile.isActive:
        q = request.GET.get("q")
        user_profile = User.objects.get(pk=request.user.id)
        description = request.POST.get("choose_description")
        message = ""
        is_choice = False
        type_interest = True
        descriptions = []

        if 'submit' in request.GET:
            if q == None or q == "":
                message = "Please enter a keyword!"
            else:
                descriptions = get_wiki_description(q)
                is_choice = True
                if len(descriptions) == 0:
                    message = "No descriptions found!"

        if "save" in request.POST:
            if description is None or description == "" or description == "Descriptions":
                request.session['description'] = None
                message = "Nothing to save!"

            else:
                existing_interest = Interest.objects.filter(user=user_profile, wiki_description=description)
                if len(existing_interest) > 0:
                    message = "You already have that interest as " + str(existing_interest[0].name)
                else:
                    new_interest = Interest.objects.create(user=user_profile, name=q, wiki_description=description)
                    new_interest.save()
                    message = "Saved: " + description + " as " + q

        return render(request, 'wiki/wiki_description.html',
                    {'message': message, "descriptions": descriptions, "q": q, "is_choice": is_choice, "type_interest":type_interest})
    else:
        return redirect('index')
