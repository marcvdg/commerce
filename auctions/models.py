from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    id = models.IntegerField(primary_key=True)

class Listing(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", default=1)
    description = models.CharField(max_length=256)
    starting_bid = models.IntegerField()
    image_url = models.CharField(blank=True, max_length=256)
    category = models.CharField(max_length=64, blank=True)
    active = models.BooleanField(default=True)
    watched_by = models.ManyToManyField('User', related_name='watchlist')

    def __str__(self):
        return f"{self.id}: {self.name}"

class Bid(models.Model):
    amount = models.IntegerField()
    timestamp = models.DateTimeField(default=now, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", default=1)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.id}: {self.user}'s' bid of {self.amount} on {self.listing}"

class Comment(models.Model):
    content = models.CharField(max_length=64)
    timestamp = models.DateTimeField(default=now, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.id}: {self.user} said \'{self.content}\' about {self.listing}"
