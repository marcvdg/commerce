from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_listing, name="add_listing"),
    path("close_listing/<int:listing_id>", views.close_listing, name="close_listing"),
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("add_bid/<int:listing_id>", views.add_bid, name="add_bid"),
    path("add_watchlist/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>", views.listing, name="listing")
]
