from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.project, name='project'), 
    path('project/<int:pk>/', views.project_detail, name='project_detail'), 
    path('contact/', views.contact, name='contact'),
]