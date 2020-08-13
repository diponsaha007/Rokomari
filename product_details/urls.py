from product_details import views
from django.urls import path

app_name = 'product_details'

urlpatterns = [
    path('product/<int:pk>/', views.product_details, name='product_details'),
    path('product/<int:pk>/update_review', views.update_review, name='update_review'),
    path('product/<int:pk>/add_review', views.add_review, name='add_review'),
    path('product/<int:pk>/delete_review', views.delete_review, name='delete_review'),
]
