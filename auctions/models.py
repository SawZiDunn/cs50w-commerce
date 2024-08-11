from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass


class Category(models.Model):
    categoryTitle = models.CharField(max_length=60)

    def __str__(self):
        return self.categoryTitle


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="userBids")
    value = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.value}$ bid by {self.user}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    price = models.ForeignKey(Bid, on_delete=models.CASCADE, blank=True, null=True, related_name="bid")
    created = models.DateTimeField(auto_now_add=True)
    photoUrl = models.CharField(max_length=1200, blank=True)
    description = models.CharField(max_length=250, blank=False)
    isOpen = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="items")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="listings")
    watchlist = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="watchlist", blank=True, null=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    comment = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", null=True, blank=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingComments", blank=True, null=True)

    def __str__(self):
        return f"{self.owner} commented on {self.listing}"