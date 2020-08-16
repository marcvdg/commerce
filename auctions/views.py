""" Mini-marktplaats """

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import (User, Bid, Listing, Comment)

#to util
def get_min_bid(listing_id):
    current_listing = Listing.objects.get(pk=listing_id)
    try:
        min_bid = Bid.objects.filter(listing__id=listing_id).order_by('-amount').first().amount
    except AttributeError:
        min_bid = current_listing.starting_bid
    return min_bid

class ListingForm(forms.Form):
    """ Form to create a new listing """
    listing_name = forms.CharField(label='Listing name', max_length=64)
    listing_desc = forms.CharField(label='Description', max_length=256)
    listing_start = forms.IntegerField(label='Starting bid', max_value=9999)

class CommentForm(forms.Form):
    """ Form to comment on a listing """
    comment_content = forms.CharField(label='Your comment', max_length=256)

class BidForm(forms.Form):
    """ Form to place a bid """
    bid_amount = forms.IntegerField(label='Your bid', max_value=9999, validators=[])
    min_bid = forms.IntegerField(label='MIN') #widget=forms.HiddenInput())

    def clean(self):
        # Don't allow bids that are below current limit
        cleaned_data = super(BidForm, self).clean()
        min_bid = cleaned_data.get('min_bid')
        bid_amount = cleaned_data.get('bid_amount')
        if min_bid >= bid_amount:
            print("WAR")
            raise ValidationError(_('Must be higher than highest bid so far..'))
        return cleaned_data


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
    highest_bid = get_min_bid(listing_id)
    if request.method == "POST":
        bidform = BidForm(request.POST)
        if bidform.is_valid():
            bid_amount = bidform.cleaned_data["bid_amount"]
            if bid_amount > highest_bid:
                newbid = Bid(user=request.user, amount=bid_amount, listing=current_listing)
                newbid.save()
            else:
                print('not high enough')
                #TO DO: error validator
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
    form = ListingForm
    if request.method == "POST":
        listing_name = request.POST["listing_name"]
        listing_desc = request.POST["listing_desc"]
        listing_start = request.POST["listing_start"]
        listing_user = request.user
        newlisting = Listing(name=listing_name,
                             user=listing_user,
                             description=listing_desc,
                             starting_bid=listing_start,
                             active=True)
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
