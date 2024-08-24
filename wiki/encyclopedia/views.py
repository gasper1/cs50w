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
    title, content = '', ''
    if request.method == 'POST':
        title = request.POST.get('title','')
        content = request.POST.get('content','')   
        if util.get_entry(title) is None:
            util.save_entry(title, content)
            return redirect("../wiki/" + title)

    return render(request, "encyclopedia/new.html", {
        'title': title,
        'content': content
    })

def edit(request, title):
    edit_title, edit_content = None, None
    if request.method == 'POST':
        edit_title = request.POST.get('title','N/A')
        edit_content = request.POST.get('content','N/A')
        if edit_content:
            util.save_entry(title, edit_content)
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": util.get_entry(title)
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

