from add_new_book import views
from django.urls import path

app_name = 'add_new_book'

urlpatterns = [
    path('add_new_book/', views.add_new, name='add_new'),
    path('add_author/', views.add_author, name='add_author'),
    path('add_publisher/', views.add_publisher, name='add_publisher'),
    path('book_added/', views.update_database, name='add_book'),
    path('send_token/', views.send_token, name='send_token'),
]
