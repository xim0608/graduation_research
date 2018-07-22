"""graduation_research URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from review_based_recommender.views import SpotListView, SpotDetailView
from review_based_recommender import views

urlpatterns = [
    # path('spots/', include('review_based_recommender.urls')),
    path('spots/', SpotListView.as_view(), name='index'),
    path('spots/<int:pk>', SpotDetailView.as_view(), name='detail'),
    path('search/', views.search),
    path('gr_admin/', admin.site.urls),
]
