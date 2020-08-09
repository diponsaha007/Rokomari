from product_list import views
from django.urls import path

app_name = 'product_list'

urlpatterns = [
    path('product_list/author/<str:query>', views.product_list_author, name='author'),
    path('product_list/genre/<str:query>', views.product_list_genre, name='genre'),
    path('product_list/publication/<str:query>', views.product_list_publisher, name='publisher'),
]

#<int:pk>/