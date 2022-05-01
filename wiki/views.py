from django.shortcuts import render
import requests


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
    q = request.GET.get("q")
    description = request.POST.get("choose_description")
    message = ""
    is_choice = False
    descriptions = []
    if request.session.get("type") == "event":
        type_event = True
    else:
        type_event = False

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
                   "type_event": type_event})
