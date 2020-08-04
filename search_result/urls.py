from search_result import views
from django.urls import path

app_name = 'search_result'

urlpatterns = [
    path('search/', views.search_result, name='search'),
]
