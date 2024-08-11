from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Category, Comment, Bid


def index(request):
    listings: list = Listing.objects.filter(isOpen=True)

    return render(request, "auctions/index.html", {
        "listings": listings,
    })


@login_required
def add(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["imageUrl"]
        user = request.user

        price = Bid(value=request.POST["startingBid"], user=user)
        price.save()

        new_list = Listing(
            title=title,
            description=description,
            price=price,
            photoUrl=image_url,
            category=Category.objects.get(categoryTitle=request.POST["category"]),
            owner=user
        )

        new_list.save()

        return HttpResponseRedirect(reverse("auctions:index"))

    return render(request, "auctions/add.html", {
        "category_list": Category.objects.all(),
    })


@login_required()
def add_watchlist(request, list_id):
    if request.method == "POST":
        current_list = Listing.objects.get(pk=list_id)
        current_list.watchlist.add(request.user)
        return HttpResponseRedirect(reverse("auctions:listing", args=(list_id,)))


@login_required()
def remove_watchlist(request, list_id):
    if request.method == "POST":
        current_list = Listing.objects.get(pk=list_id)
        current_list.watchlist.remove(request.user)
        return HttpResponseRedirect(reverse("auctions:listing", args=(list_id,)))


@login_required()
def watchlist(request):
    user = request.user
    listings = user.watchlist.all()

    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })


def category(request):
    if request.method == "POST":
        category = Category.objects.get(categoryTitle=request.POST["category"])

        return render(request, "auctions/index.html", {
            "listings": Listing.objects.filter(isOpen=True, category=category),
            "category_list": Category.objects.all(),
        })

    return render(request, "auctions/category.html", {
        "category_list": Category.objects.all(),
    })


def listing(request, list_id):
    current_list = Listing.objects.get(pk=list_id)
    comments = current_list.listingComments.all()
    isInWatchlist = request.user in current_list.watchlist.all()
    # bids = Bid.objects.filter(bid=current_list)
    # print(len(bids), bids)

    return render(request, "auctions/listing.html", {
        "listing": current_list,
        "isInWatchlist": isInWatchlist,
        "comments": comments,
    })


def place_bid(request, list_id):
    new_bid = float(request.POST["bid"])
    current_list = Listing.objects.get(pk=list_id)

    comments = current_list.listingComments.all()
    isInWatchlist = request.user in current_list.watchlist.all()

    if new_bid <= current_list.price.value:

        return render(request, "auctions/listing.html", {
            "listing": current_list,
            "isInWatchlist": isInWatchlist,
            "comments": comments,
            "message": "Bid Update Failed!"
        })

    updated_bid = Bid(value=new_bid, user=request.user)
    updated_bid.save()
    current_list.price = updated_bid
    current_list.save()

    return render(request, "auctions/listing.html", {
            "listing": current_list,
            "isInWatchlist": isInWatchlist,
            "comments": comments,
            "message": "Successfully Updated Bid!"
        })


@login_required()
def close_auction(request, list_id):
    current_list = Listing.objects.get(pk=list_id)
    current_list.isOpen = False
    current_list.save()
    return HttpResponseRedirect(reverse("auctions:index"))


@login_required()
def won_auction(request):
    listings = Listing.objects.filter(isOpen=False)

    listings: list = [each for each in listings if each.price.user == request.user]
    # for each in listings:
    #     if each.price.user == user:
    #         new_listing.append(each)

    return render(request, "auctions/index.html", {
        "listings": listings,
    })


@login_required()
def comment(request, list_id):
    if request.method == "POST":
        comment = request.POST["comment"]
        owner = request.user
        current_listing = Listing.objects.get(pk=list_id)
        new_comment = Comment(comment=comment, owner=owner, listing=current_listing)
        new_comment.save()
        return HttpResponseRedirect(reverse("auctions:listing", args=(list_id,)))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
