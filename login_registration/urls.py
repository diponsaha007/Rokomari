from login_registration import views
from django.urls import path

app_name = 'login_registration'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('registration/', views.registration, name='registration'),
    path('admin/', views.login_admin, name='login_admin'),
    path('admin/logout/', views.logout_admin, name='logout_admin'),
    path('admin_registration/', views.registration_admin, name='registration_admin'),
]