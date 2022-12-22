from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name = "create"),
    path("auction/<str:id>", views.auction, name = "auction"),
    path("close/<str:id>", views.close, name = "close"),
    path("add_watchlist/<str:listing>", views.add_watchlist, name= "add_watchlist"),
    path("remove_watchlist/<str:listing>", views.remove_watchlist, name= "remove_watchlist"),
    path("watchlist", views.watchlist, name ="watchlist"),
    path("categories", views.category, name ="categories"),
    path("categories/<str:category>", views.categorypage, name ="categoriespage")
]
