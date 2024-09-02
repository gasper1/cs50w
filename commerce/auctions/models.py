from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    pass


class ListingCategories(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=200)
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", default='')
    starting_price = models.FloatField()
    created_at = models.DateTimeField(default=now)
    imgURL = models.URLField(blank=True, default='')
    category = models.ForeignKey(ListingCategories, on_delete=models.CASCADE, related_name="listings")
    watchlisted_by = models.ManyToManyField(User, related_name="watchlist_items")

    def __str__(self) -> str:
        return f"{self.title} - {self.category}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.FloatField()
    created_at = models.DateTimeField(default=now)
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", default="")


class Comment(models.Model):
    text = models.TextField(max_length=200)