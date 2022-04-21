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
    descriptions = []

    if 'submit' in request.GET:
        if q == None or q == "":
            message = "Please enter a keyword."
        else:
            descriptions = get_wiki_description(q)

    if "save" in request.POST:
        if description is None or description == "" or description == "Descriptions":
            request.session['description'] = None
        else:
            request.session['description'] = q + ": " + description

    return render(request, 'wiki/wiki_description.html',
                  {'message': message, "descriptions": descriptions, "q": q})
