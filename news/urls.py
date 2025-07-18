from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    path('category/<slug:slug>/', views.category_view, name='category_view'),
    path('subscribe/', views.subscribe, name='subscribe'),
]
