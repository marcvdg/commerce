from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext as _

from .models import (Listing)

class ListingForm(ModelForm):
    """ Form to create a new listing """
    class Meta:
        model = Listing
        fields = ['user', 'name', 'description', 'starting_bid', 'category', 'image_url']
        widgets = {'user': forms.HiddenInput()}

class CommentForm(forms.Form):
    """ Form to comment on a listing """
    comment_content = forms.CharField(label='Your comment', max_length=256)

class BidForm(forms.Form):
    """ Form to place a bid """
    bid_amount = forms.IntegerField(label='Your bid', max_value=9999, validators=[])
    min_bid = forms.IntegerField(label='MIN', widget=forms.HiddenInput())

    def clean(self):
        # Don't allow bids that are below current limit
        cleaned_data = super(BidForm, self).clean()
        min_bid = cleaned_data.get('min_bid')
        bid_amount = cleaned_data.get('bid_amount')
        if min_bid >= bid_amount:
            raise ValidationError(_('Must be higher than highest bid so far.'))
        return cleaned_data