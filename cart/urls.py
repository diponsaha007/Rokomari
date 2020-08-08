from cart import views
from django.urls import path

app_name = 'cart'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:pk>/', views.remove_book, name='remove_book'),
    path('cart/add/<int:pk>/', views.add_book, name='add_book'),
]
