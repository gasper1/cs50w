from django.contrib import admin
from .models import Listing, ListingCategories, Bid, Comment

# Register your models here.
admin.site.register(Listing)
admin.site.register(ListingCategories)
admin.site.register(Bid)
admin.site.register(Comment)