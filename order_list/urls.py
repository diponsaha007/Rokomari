from order_list import views
from django.urls import path

app_name = 'order_list'

urlpatterns = [
    path('my_orders/', views.order_list, name='order_list'),
]
