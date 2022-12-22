from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass
class Bids(models.Model):
    user = models.ForeignKey(User, related_name=("bidder"), on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    bid = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.bid)

class Comments(models.Model):   
    user = models.ForeignKey(User, related_name=("commentor"), on_delete=models.CASCADE)
    comment = models.TextField()
    def __str__(self):
        return self.comment

class Category(models.Model):
    name = models.CharField(primary_key = True, max_length=50)
    def __str__(self):
        return self.name

class Listings(models.Model):
    seller=models.ForeignKey(User, related_name= ("seller"), on_delete=models.CASCADE)
    title  = models.CharField(max_length=200)
    starting = models.DecimalField(max_digits=15, decimal_places=2)
    bid = models.ManyToManyField(Bids, related_name='all_bids')
    description = models.CharField(max_length=1000)
    datetime = models.DateTimeField(auto_now_add = True)
    category = models.ManyToManyField(Category, related_name = ("cat"))
    winningUser = models.ForeignKey(User, null= True, related_name=("winner"), on_delete=models.CASCADE)
    current_bid = models.ForeignKey(Bids,null=True, related_name=("highest_bidder"), on_delete=models.CASCADE)
    image = models.ImageField( upload_to='images', blank = True, null = True)
    comments = models.ManyToManyField(Comments, related_name=("comments"))
    def __str__(self):
        return self.title

class Watchlist(models.Model):
    user = models.ForeignKey(User, related_name=("user"), on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listings, related_name=("listing"))
    
    def __str__(self):
        return self.user + self.listing

