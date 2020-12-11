from my_account import views
from django.urls import path

app_name = 'my_account'

urlpatterns = [
    path('my_account/', views.my_account, name='my_account'),
    path('admin_account/', views.admin_account, name='admin_account'),
    path('my_account/update/personal/', views.update_personal, name='update_personal'),
    path('my_account/update/contact/', views.update_contact, name='update_contact'),
    path('my_account/update/photo/', views.update_photo, name='update_photo'),
    path('admin_account/update/photo/', views.update_photo_admin, name='update_photo_admin'),
    path('admin_account/update/personal/', views.update_personal_admin, name='update_personal_admin'),
]
