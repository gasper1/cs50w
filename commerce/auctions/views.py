from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, ListingCategories, Bid


class CreateForm(forms.Form):
    title = forms.CharField(label="Title", max_length=64)
    category = forms.ModelChoiceField(queryset=ListingCategories.objects.all(), label="Category")
    description = forms.CharField(widget=forms.Textarea, label="Description")
    starting_price = forms.FloatField()


class BidForm(forms.Form):
    price = forms.FloatField()


def index(request):
    listings = []
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        listings = user.listings.all()

    return render(request, "auctions/index.html", {
        "listings": listings
    })


def item(request, id):
    user = User.objects.get(pk=request.user.id)
    listing = Listing.objects.get(pk=id)
    bid_form = BidForm()
    starting_price_bid = Bid(listing=listing, price=listing.starting_price, by_user=listing.by_user, created_at=listing.created_at)
    return render(request, "auctions/item.html", {
        "listing": listing,
        "watched_by_user": user in listing.watchlisted_by.all(),
        "bid_form": bid_form,
        "bids": [starting_price_bid] + [bid for bid in Bid.objects.filter(by_user=user, listing=listing)]
    })


def place_bid(request, id):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        form = BidForm(request.POST)
        if form.is_valid():
            bid = Bid(
                by_user = user,
                listing = Listing.objects.get(pk=id),
                price = form.cleaned_data["price"]
            )
            bid.save()
    return HttpResponseRedirect(reverse("item", kwargs={'id':id}))


def new(request):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        form = CreateForm(request.POST)
        if form.is_valid():
            listing = Listing(
                title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                category=form.cleaned_data['category'],
                starting_price = form.cleaned_data["starting_price"],
                by_user = user
            )
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = CreateForm()
    return render(request, "auctions/new.html", {
        "form": form
    })


def categories(request, id='None'):
    if id != 'None':
        category = ListingCategories.objects.get(pk=id)
        category_name = category.name
        listings = category.listings.all()
    else:
        category_name = ''
        listings = ''
    return render(request, "auctions/categories.html", {
        "categories": ListingCategories.objects.all(),
        "category_name": category_name,
        "listings": listings
    })


def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    return render(request, "auctions/watchlist.html", {
        "listings": user.watchlist_items.all()
    })


def watch_unwatch_item(request, id):
    user = User.objects.get(pk=request.user.id)
    listing = Listing.objects.get(pk=id)
    watched_by_user = (user in listing.watchlisted_by.all())
    if watched_by_user:
        listing.watchlisted_by.remove(user)
    else:
        listing.watchlisted_by.add(user)
    watched_by_user = not watched_by_user
    return render(request, "auctions/item.html", {
        "listing": listing,
        "watched_by_user": watched_by_user
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
