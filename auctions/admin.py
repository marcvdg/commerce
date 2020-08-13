from django.contrib import admin
from .models import User, Listing, Bid, Comment

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")
    pass

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user")

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)

