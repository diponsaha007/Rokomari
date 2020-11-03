from admin_dashboard import views
from django.urls import path

app_name = 'admin_dashboard'

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
