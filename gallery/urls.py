from django.urls import path
from gallery import views

urlpatterns = [
    path('', views.gallery_view, name='gallery'),
]