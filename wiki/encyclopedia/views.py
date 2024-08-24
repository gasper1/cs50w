from django.shortcuts import render
from markdown2 import Markdown
from django.shortcuts import redirect
from django.urls import reverse
from django.core.files import File

from . import util

from random import randint


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

def new(request):
    page_title, page_content = '', ''
    if request.method =='POST':
        page_title = request.POST.get('page_title','')
        page_content = request.POST.get('page_content','')   

    #TODO check if entry is already stored
    
    #TODO if not, create a new .md file in the entries page
    

    return render(request, "encyclopedia/new.html", {
        'page_title': page_title,
        'page_content': page_content
    })

def edit(request, title):
    return render(request, "encyclopedia/edit.html", {
        "page_title": title,
        "page_content": util.get_entry(title)
    })

def random(request):
    markdowner = Markdown()
    entries = util.list_entries()
    rand_idx = randint(0, len(entries)-1)
    title = entries[rand_idx]
    return render(request, "encyclopedia/wiki.html", {
        "title": title,
        "content": markdowner.convert(util.get_entry(title))
    })

