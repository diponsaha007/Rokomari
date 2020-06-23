from rokomariapp import views
from django.urls import path

app_name = 'rokomariapp'

urlpatterns = [
    path('', views.index, name='index'),
]
