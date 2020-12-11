from showdata import views
from django.urls import path

app_name = 'showdata'

urlpatterns = [
    path('book_database/', views.search_result, name='showdata'),
    path('deleted_book_database/', views.deleted_books, name='deleted_books'),
    path('author_database/', views.search_result_author, name='showdata_author'),
    path('publisher_database/', views.search_result_publisher, name='showdata_publisher'),
    path('customer_database/', views.customer_database, name='customer_database'),
    path('admin_database/', views.admin_database, name='admin_database'),
    path('order_database/', views.order_database, name='order_database'),
    path('show_tokens/', views.show_tokens, name='show_tokens'),
    path('deleted/<int:pk>', views.delete_book, name='delete_book'),
    path('deleted_author/<int:pk>', views.delete_author, name='delete_author'),
    path('deleted_publisher/<int:pk>', views.delete_publisher, name='delete_publisher'),
    path('update/<int:pk>', views.update_book, name='update_book'),
    path('restore_book/<int:pk>', views.restore_book, name='restore_book'),
    path('mark_delivered/<int:pk>', views.mark_as_delivered, name='mark_as_delivered'),
    path('order_details/<int:pk>', views.show_order_details, name='show_order_details'),
]
