""" Mini-marktplaats """

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

from .models import (User, Bid, Listing, Comment)
from .util import (get_min_bid)
from .forms import (ListingForm, BidForm, CommentForm)


def index(request):
    """ Homepage, displaying open and closed auctions """
    listings_db = Listing.objects.all()
    active_listings = []
    closed_listings = []
    for row in listings_db:
        if row.active:
            active_listings.append(model_to_dict(row))
        else:
            closed_listings.append(model_to_dict(row))
    return render(request, "auctions/index.html", {'active_listings': active_listings,
                                                   'closed_listings': closed_listings
                                                   })

def listing(request, listing_id):
    """ Listing page, displaying description, bid and content """

    # Get all the page's variables
    current_user = str(request.user)
    current_listing = Listing.objects.get(pk=listing_id)
    active = current_listing.active
    bids = Bid.objects.filter(listing__id=listing_id)
    comments = Comment.objects.filter(listing__id=listing_id)

    # Set forms
    commentform = CommentForm()
    bidform = BidForm(initial={"min_bid":get_min_bid(listing_id)})

    # Check if listing belongs to user
    mylisting = (current_listing.user.username == current_user)

    # Generate watch button
    watchers = current_listing.watched_by.all()
    if request.user in watchers:
        watchbutton = 'Remove from watchlist'
    else:
        watchbutton = 'Add to watchlist'

    # Decide the winner if inactive
    try:
        winner = Bid.objects.filter(listing__id=listing_id).order_by('-amount').first().user
    except AttributeError:
        winner = "no one"

    if request.method == "POST":
        bidform = BidForm(request.POST)
        if bidform.is_valid():
            bid_amount = bidform.cleaned_data["bid_amount"]
            newbid = Bid(user=request.user, amount=bid_amount, listing=current_listing)
            newbid.save()

    # Render the page
    return render(request, "auctions/listing.html", {'id': listing_id,
                                                     'listing': current_listing,
                                                     'bids': bids,
                                                     'bidform': bidform,
                                                     'comments': comments,
                                                     'commentform': commentform,
                                                     'watchbutton': watchbutton,
                                                     'mylisting': mylisting,
                                                     'active': active,
                                                     'winner': winner
                                                    })

def categories(request):
    listings = Listing.objects.all()
    category_set = {"No category": []}
    for listing in listings:
        if listing.category == "":
            category_set["No category"].append(listing)
        else: 
            try:
                category_set[listing.category].append(listing)
            except KeyError:
                category_set[listing.category] = [listing]
    print(category_set)
    return render(request, "auctions/categories.html", {'categories': category_set})

@login_required
def add_comment(request, listing_id):
    current_listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        commentform = CommentForm(request.POST)
        if commentform.is_valid():
            comment_content = commentform.cleaned_data["comment_content"]
            newcomment = Comment(user=request.user,
                                 listing=current_listing,
                                 content=comment_content)
            newcomment.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def watchlist(request):
    user = User.objects.get(username=request.user)
    current_watchlist = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {'watchlist': current_watchlist})

@login_required
def close_listing(request, listing_id):
    current_user = str(request.user)
    current_listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        if current_listing.user.username == current_user:
            current_listing.active = False
            current_listing.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def add_bid(request, listing_id):
    current_listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        bidform = BidForm(request.POST)
        if bidform.is_valid():
            bid_amount = bidform.cleaned_data["bid_amount"]
            newbid = Bid(user=request.user, amount=bid_amount, listing=current_listing)
            newbid.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def add_watchlist(request, listing_id):
    current_listing = Listing.objects.get(pk=listing_id)
    watchers = current_listing.watched_by.all()
    if request.method == "POST":
        if request.user in watchers:
            current_listing.watched_by.remove(request.user)
        else:
            current_listing.watched_by.add(request.user)
        print(watchers)
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def add_listing(request):
    form = ListingForm(initial={"user":request.user})
    if request.method == "POST":
        newlisting = ListingForm(request.POST)
        newlisting.save()
    return render(request, "auctions/newlisting.html", {'form': form})

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
