from add_new_book import views
from django.urls import path

app_name = 'add_new_book'

urlpatterns = [
    path('add_new_book/', views.add_new, name='add_new'),
    path('book_added/', views.update_database, name='add_book'),
]
