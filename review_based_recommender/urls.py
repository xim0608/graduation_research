from django.urls import path
from review_based_recommender import views

app_name = 'cms'
urlpatterns = [
    path('search/', views.search, name='search_index'),
]