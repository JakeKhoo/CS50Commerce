from django.contrib import admin
from .models import Bids, Listings, User, Comments, Category, Watchlist
admin.site.register(Bids)
admin.site.register(Listings)
admin.site.register(User)
admin.site.register(Comments)
admin.site.register(Category)
admin.site.register(Watchlist)

# Register your models here.
