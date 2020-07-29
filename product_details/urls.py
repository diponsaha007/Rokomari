from product_details import views
from django.urls import path

app_name = 'product_details'

urlpatterns = [
    path('product/<int:pk>/', views.product_details, name='product_details'),
]
