from wishlist import views
from django.urls import path

app_name = 'wishlist'

urlpatterns = [
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/remove/<int:pk>/', views.remove_book, name='remove_book'),
    path('wishlist/add/<int:pk>/', views.add_book, name='add_book'),
]
