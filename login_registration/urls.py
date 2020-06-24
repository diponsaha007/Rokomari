from login_registration import views
from django.urls import path

app_name = 'login_registration'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('registration/', views.registration, name='registration'),
]