from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("item/<str:id>", views.item, name="item"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:id>", views.categories, name="categories"),
    path("new", views.new, name="new"),
    path("place_bid/<str:id>", views.place_bid, name="place_bid"),
    path("watch_unwatch_item/<str:id>", views.watch_unwatch_item, name="watch_unwatch_item")
]
