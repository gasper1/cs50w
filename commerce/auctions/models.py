from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class ListingCategories(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=200)
    byUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", default='')
    startingPrice = models.FloatField()
    imgURL = models.URLField(blank=True, default='')
    category = models.ForeignKey(ListingCategories, on_delete=models.CASCADE, related_name="listings")

    def __str__(self) -> str:
        return f"{self.title} - {self.category}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.FloatField()


class Comment(models.Model):
    text = models.TextField(max_length=200)