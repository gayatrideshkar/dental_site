from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('treatments/', views.treatments, name='treatments'),
    path('gallery/', views.gallery, name='gallery'),
    path('posts/', views.posts, name='posts'),
    path('contact/', views.contact, name='contact'),

    # Services
    path('services/', views.services_list, name='services_list'),
    path('services/<slug:slug>/', views.services_detail, name='services_detail'),
]
