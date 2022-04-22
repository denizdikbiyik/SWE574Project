from django.shortcuts import render
import requests


def get_wiki_description(query):
    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "tr",
        "search": query
    }
    r = requests.get(API_ENDPOINT, params=params)
    json_object = r.json()
    descriptions = []
    for i in range(len(json_object)):
        descriptions.append(r.json()["search"][i]["description"])
    return descriptions


def list_descriptions(request):
    q = request.GET.get("q")
    description = request.POST.get("choose_description")
    message = ""
    is_choice = False
    descriptions = []
    if request.session["type"] == "event":
        type_event = True
    else:
        type_event = False

    if 'submit' in request.GET:
        if q == None or q == "":
            message = "Please enter a keyword."
        else:
            descriptions = get_wiki_description(q)
            is_choice = True

    if "save" in request.POST:
        if description is None or description == "" or description == "Descriptions":
            request.session['description'] = None
        else:
            request.session['description'] = q + " as a(n) " + description
            message = "Saved: " + request.session['description']

    return render(request, 'wiki/wiki_description.html',
                  {'message': message, "descriptions": descriptions, "q": q, "is_choice": is_choice,
                   "type_event": type_event})
