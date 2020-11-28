from showdata import views
from django.urls import path

app_name = 'showdata'

urlpatterns = [
    path('book_database/', views.search_result, name='showdata'),
    path('author_database/', views.search_result_author, name='showdata_author'),
    path('publisher_database/', views.search_result_publisher, name='showdata_publisher'),
    path('deleted/<int:pk>', views.delete_book, name='delete_book'),
    path('deleted_author/<int:pk>', views.delete_author, name='delete_author'),
    path('deleted_publisher/<int:pk>', views.delete_publisher, name='delete_publisher'),
    path('update/<int:pk>', views.update_book, name='update_book'),
]
