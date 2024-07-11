from django.urls import path
from gallery import views

urlpatterns = [
    path('', views.gallery_view, name='gallery'),
    path('upload_image/', views.upload_image, name='upload_image'),
]