"""Rokomari URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("rokomariapp.urls", namespace="rokomariapp")),
    path('', include("login_registration.urls", namespace="login_registration")),
    path('', include("product_details.urls", namespace="product_details")),
    path('', include("search_result.urls", namespace="search_result")),
    path('', include("cart.urls", namespace="cart")),
    path('', include("wishlist.urls", namespace="wishlist")),
    path('', include("product_list.urls", namespace="product_list")),
    path('', include("my_account.urls", namespace="my_account")),
    path('', include("order_list.urls", namespace="order_list")),
    path('', include("add_new_book.urls", namespace="add_new_book")),
    path('admin/', admin.site.urls),
]
