from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

from .models import (User, Bid, Listing, Comment)

class ListingForm(forms.Form):
    listing_name = forms.CharField(label='Listing name', max_length=64)
    listing_desc = forms.CharField(label='Description', max_length=256)
    listing_start = forms.IntegerField(label='Starting bid', max_value=9999)

class CommentForm(forms.Form):
    comment_content = forms.CharField(label='Your comment', max_length=256)

class BidForm(forms.Form):
    bid_amount = forms.IntegerField(label='Your bid', max_value=9999)
    
def index(request):
    listings_db = Listing.objects.all()
    listings = []
    for row in listings_db:
        listings.append(model_to_dict(row))
    return render(request, "auctions/index.html", {'listings': listings})

#change template to restrict editing
def listing(request, id):
    listing = Listing.objects.get(pk=id)
    user = request.user
    bids = Bid.objects.filter(listing__id=id)
    comments = Comment.objects.filter(listing__id=id)
    if request.method == "POST":
        if "comment_content" in request.POST:
            commentform = CommentForm(request.POST)
            bidform = BidForm()
            if commentform.is_valid():
                
                comment_content = commentform.cleaned_data["comment_content"]
                newcomment = Comment(user=user, listing=listing, content=comment_content) 
                newcomment.save()
        elif "bid_amount" in request.POST:
            bidform = BidForm(request.POST)
            commentform = CommentForm()     
            if bidform.is_valid():
                bid_amount = bidform.cleaned_data["bid_amount"]
                newbid = Bid(user=request.user, amount=bid_amount, listing=listing)
                newbid.save()
        else:
            pass #add to watchlist
        return render(request, "auctions/listing.html", {'listing': listing, 'bids': bids, 'bidform': bidform, 'comments': comments, 'commentform': commentform})
    else:
        commentform = CommentForm()
        bidform = BidForm()
        return render(request, "auctions/listing.html", {'listing': listing, 'bids': bids, 'bidform': bidform, 'comments': comments, 'commentform': commentform})

@login_required
def add_comment(request):
    pass

@login_required
def add_bid(request):
    pass

@login_required
def add_to_watchlist(request):
    pass

@login_required
def add_listing(request):
    form = ListingForm
    if request.method == "POST":
        listing_name = request.POST["listing_name"]
        listing_desc = request.POST["listing_desc"]
        listing_start = request.POST["listing_start"]
        listing_user = request.user
        newlisting = Listing(name=listing_name,user=listing_user,description=listing_desc,starting_bid=listing_start,active=True)
        newlisting.save()
    return render(request, "auctions/newlisting.html",  {'form': form})

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
