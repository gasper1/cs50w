from django.shortcuts import render
from markdown2 import Markdown
from django.shortcuts import redirect
from django.urls import reverse

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, title):
    markdowner = Markdown()
    return render(request, "encyclopedia/wiki.html", {
        "title": title,
        "content": markdowner.convert(util.get_entry(title))
    })

def search(request):
    query = request.GET.get('q','')
    entries = [entry for entry in util.list_entries() if query.lower() in entry.lower()]
    if len(entries) == 1:
        return redirect("/wiki/" + entries[0])
    return render(request, "encyclopedia/search.html", {
        "query": query, 
        "entries": entries
    })

