from my_account import views
from django.urls import path

app_name = 'my_account'

urlpatterns = [
    path('my_account/', views.my_account, name='my_account'),
    path('my_account/update/personal/', views.update_personal, name='update_personal'),
    path('my_account/update/contact/', views.update_contact, name='update_contact'),
    path('my_account/update/photo/', views.update_photo, name='update_photo'),
]
