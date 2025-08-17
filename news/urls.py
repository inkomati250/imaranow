from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('category/<slug:slug>/', views.category_view, name='category_view'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    path('', views.home, name='home'),
]
