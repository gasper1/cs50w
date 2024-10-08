from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max
from django.utils.http import urlencode

from .models import User, Listing, ListingCategories, Bid, Comment


""" FORMS """

class CreateForm(forms.Form):
    title = forms.CharField(label="Title", max_length=64)
    category = forms.ModelChoiceField(queryset=ListingCategories.objects.all(), label="Category")
    description = forms.CharField(widget=forms.Textarea, label="Description")
    img_url = forms.URLField()
    starting_price = forms.FloatField()


class BidForm(forms.Form):
    def __init__(self, *args, **kwargs):
        max_bid = kwargs.pop('max_bid', 0)  # Pop the max_bid from kwargs, default to 0 if not provided
        super().__init__(*args, **kwargs)  # Call the parent constructor
        self.fields['price'].min_value = max_bid + 0.01  # Dynamically set the min_value
        self.fields['price'].widget.attrs['min'] = max_bid + 0.01  # Set the HTML min attribute for client-side validation

    price = forms.FloatField(min_value=0.01)


class CommentForm(forms.Form):
    comment = forms.CharField(max_length=200)



""" AUTHENTICATION FUNCTIONS """


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




""" NAVIGATION / PAGE LOADERS """


def index(request):
    listings = []
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        listings = Listing.objects.all()

    return render(request, "auctions/index.html", {
        "listings": listings
    })


def item(request, id):
    user = User.objects.get(pk=request.user.id)
    listing = Listing.objects.get(pk=id)
    max_bid = listing.bids.aggregate(Max("price", default=listing.starting_price))["price__max"]
    try:
        max_bidder = listing.bids.get(price=max_bid).by_user
    except Bid.DoesNotExist:
        max_bidder = None
    bid_form = BidForm(max_bid=max_bid)
    comment_form = CommentForm()
    starting_price_bid = Bid(listing=listing, price=listing.starting_price, by_user=listing.by_user, created_at=listing.created_at)
    return render(request, "auctions/item.html", {
        "listing": listing,
        "watched_by_user": user in listing.watchlisted_by.all(),
        "bid_form": bid_form,
        "bids": [starting_price_bid] + [bid for bid in listing.bids.all()],
        "comment_form": comment_form,
        "comments": [comment for comment in listing.comments.all()],
        "max_bidder": max_bidder,
        "max_bid": max_bid
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




""" DB MODIFIERS """


def new(request):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        form = CreateForm(request.POST)
        if form.is_valid():
            listing = Listing(
                title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                category=form.cleaned_data['category'],
                imgURL=form.cleaned_data['img_url'],
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


def watch_unwatch_item(request, id):
    user = User.objects.get(pk=request.user.id)
    listing = Listing.objects.get(pk=id)
    watched_by_user = (user in listing.watchlisted_by.all())
    if watched_by_user:
        listing.watchlisted_by.remove(user)
    else:
        listing.watchlisted_by.add(user)
    watched_by_user = not watched_by_user
    query_kwargs={"watched_by_user": watched_by_user}
    return HttpResponseRedirect(reverse("item", kwargs={"id": id}) + '?' + urlencode(query_kwargs))


def place_bid(request, id):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        listing = Listing.objects.get(pk=id)
        max_bid = listing.bids.aggregate(Max("price", default=listing.starting_price))["price__max"]
        form = BidForm(request.POST, max_bid=max_bid)
        if form.is_valid() and user != listing.by_user:
            bid = Bid(
                price = form.cleaned_data["price"],
                by_user = user,
                listing = listing
            )
            bid.save()
    return HttpResponseRedirect(reverse("item", kwargs={'id':id}))


def comment(request, id):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        listing = Listing.objects.get(pk=id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                text = form.cleaned_data["comment"],
                by_user = user,
                listing = listing
            )
            comment.save()
    return HttpResponseRedirect(reverse("item", kwargs={'id':id}))


def close_bid(request, id):
    user = User.objects.get(pk=request.user.id)
    listing = Listing.objects.get(pk=id)
    if listing.by_user == user:
        listing.status = Listing.CLOSED
        listing.save()
    return HttpResponseRedirect(reverse("item", kwargs={'id':id}))
