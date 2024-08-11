from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("addListing", views.add, name="add"),
    path("category", views.category, name="category"),
    path("listing/<int:list_id>", views.listing, name="listing"),
    path("bid/<int:list_id>", views.place_bid, name="place_bid"),
    path("comment/<int:list_id>", views.comment, name="comment"),
    path("addWatchlist/<int:list_id>", views.add_watchlist, name="add_watchlist"),
    path("removeWatchlist/<int:list_id>", views.remove_watchlist, name="remove_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("closeAuction/<int:list_id>", views.close_auction, name="close_auction"),
    path("wonAuction", views.won_auction, name="won_auction"),
]
