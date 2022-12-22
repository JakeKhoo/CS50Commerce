from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from .models import User, Listings, Watchlist, Comments, Bids, Category
from django.contrib import messages

Categories = (('None',"None"),('Fashion',"Fashion"), ('Electronics',"Electronics"), ('Household',"Household"), ('Aquarium',"Aquarium"))
class CreateForm(forms.Form):
    title = forms.CharField(label= 'Title \n', widget = forms.TextInput(attrs = {
        "placeholder": "Title of the Listing",
        "style" : 'width: 60%;'
    }))

    description = forms.CharField(label='', widget = forms.Textarea(attrs = {
        "placeholder" : "Type the description here",
         "style" : 'width: 60%; height:400px'
    }))

    categories = forms.CharField(label= '',  widget = forms.Select(choices = Categories))

    bid = forms.CharField(label = "", widget = forms.TextInput(attrs={
        "placeholder": "your bid",
        "style" : 'width: 60%;'
    }))

    image = forms.URLField(label = "", required = False, widget = forms.URLInput(attrs={
        "placeholder": "Image URL",
        "style" : 'width: 60%;'
    }))

class BiddingForm(forms.Form):
    bid = forms.CharField(label = "", widget = forms.TextInput(attrs={
        "placeholder": "your bid",
        "style" : 'width: 100px;'
    }))

class CommentForm(forms.Form):
    comment = forms.CharField(label='', widget = forms.Textarea(attrs = {
        "placeholder" : "Type the description here",
        "style" : 'width: 60%; height:400px'
    }))

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listings.objects.all()
    })

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
            w = Watchlist(
                user = user
            )
            w.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required()
def create(request):
    if request.method == "POST":
        f = CreateForm(request.POST)
        if f.is_valid():
            title = f.cleaned_data["title"]
            description = f.cleaned_data["description"]
            bid = f.cleaned_data["bid"]
            image = f.cleaned_data["image"]
            cats = f.cleaned_data["categories"]

            listing = Listings(
                seller = User.objects.get(pk=request.user.id),
                title = title,
                description = description,
                starting = float(bid),
                image = image
            )
            listing.save()
            if cats != "None":
                categ = Category.objects.get(name = cats)
                listing.category.add(categ)
                listing.save()


            print(listing.datetime)
            return  HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html",{
                "createform" : CreateForm()
            })
    else:
        return render(request, "auctions/create.html",{
            "createform" : CreateForm()
        })

@login_required()
def auction(request,id):
    listing = Listings.objects.get(pk=id)
    comments = listing.comments.all()
    num = Bids.objects.filter(all_bids = listing).count()
    username = False
    seller = False
    winner = False
    closed = False
    if listing.current_bid != None:
        if listing.current_bid.user == request.user:
            username = True
        if listing.winningUser == request.user:
            winner = True
    if listing.winningUser != None:
        closed = True
    if listing.seller == request.user:
        seller = True
    if request.method == "GET":
        return render(request,"auctions/auction.html",{
            "listing" : listing,
            "id" : id,
            "num_bids" : num,
            "BiddingForm" : BiddingForm(),
            "username" : username,
            "seller" : seller,
            "winner" : winner,
            "closed" : closed,
            "CommentForm" : CommentForm(),
            "comments" : comments
        })
    else:
        if request.method == "POST" :
            form = BiddingForm(request.POST)
            comment = CommentForm(request.POST)
            if comment.is_valid():
                newcomment = Comments(
                    user = User.objects.get(pk=request.user.id),
                    comment = comment.cleaned_data["comment"]
                )
                newcomment.save()
                listing.comments.add(newcomment)
                return HttpResponseRedirect(reverse("auction", kwargs={'id':id})) 
            if form.is_valid():
                bid = float(form.cleaned_data["bid"])
                if listing.current_bid is None :
                    current = 1000000000000000
                else:
                    current = listing.current_bid.bid
                if ((bid >= listing.starting and num == 0) or (bid>current)):
                    newBid = Bids(
                        user = User.objects.get(pk=request.user.id),
                        active = True,  
                        bid = bid
                    )
                    newBid.save()
                    listing.bid.add(newBid)
                    listing.current_bid = newBid
                    listing.save()
                    return HttpResponseRedirect(reverse("index"))
                else:
                    messages.warning(request,"Invalid Bid")
                    return render(request,"auctions/auction.html",{
                    "listing" : listing,
                    "id" : id,
                    "num_bids" : num,
                    "BiddingForm" : BiddingForm(),
                    "username" : username,
                    "seller" : seller,
                    "winner" : winner,
                    "closed" : closed,
                    "CommentForm" : CommentForm(),
                    "comments" : comments
                    })


        else:
            messages.warning(request,"Invalid Bid")
            return render(request,"auctions/auction.html",{
            "listing" : listing,
            "id" : id,
            "num_bids" : num,
            "BiddingForm" : BiddingForm(),
            "username" : username,
            "seller" : seller,
            "winner" : winner,
            "closed" : closed,
            "CommentForm" : CommentForm(),
            "comments" : comments
            })

def close(request, id):
    listing = Listings.objects.get(pk=id)
    listing.winningUser = listing.current_bid.user
    listing.save()
    return render(request, "auctions/close.html")

def add_watchlist(request, listing):
    user = User.objects.get(pk=request.user.id)
    listing_set = Watchlist.objects.get(user=user).listing.all()
    if listing not in listing_set:
        w = Watchlist.objects.get(user=user)
        w.listing.add(Listings.objects.get(pk=listing))
        w.save()
    return HttpResponseRedirect(reverse("watchlist"))
 

def remove_watchlist(request, listing):
    user = User.objects.get(pk=request.user.id)
    listing_set = Watchlist.objects.get(user=user).listing.all()
    L = Listings.objects.get(pk=listing)

    if L in listing_set:
        print('hi')
        w = Watchlist.objects.get(user=user)
        w.listing.remove(Listings.objects.get(pk=listing))
        w.save()
    return HttpResponseRedirect(reverse("watchlist"))

@login_required()
def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    listing_set = Watchlist.objects.get(user=user).listing.all()
    return render(request,"auctions/watchlist.html", {
        "userwatchlist": listing_set
    })

def category(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories" : categories
    })

def categorypage(request, category):
    c = Category.objects.get(name=category)
    listing_set = Listings.objects.filter(category=c).all()
    return render(request, "auctions/categorypage.html", {
        "set" : listing_set,
        "name": category
    })