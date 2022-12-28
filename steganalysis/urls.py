from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('analyze-image',views.image_analysis),
    path('hide-data',views.hideData),
]