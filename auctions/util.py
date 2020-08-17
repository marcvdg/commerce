from .models import (Listing, Bid)

def get_min_bid(listing_id):
    current_listing = Listing.objects.get(pk=listing_id)
    try:
        min_bid = Bid.objects.filter(listing__id=listing_id).order_by('-amount').first().amount
    except AttributeError:
        min_bid = current_listing.starting_bid
    return min_bid
    