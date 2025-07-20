from django.urls import path
from . import views

app_name = 'edocuments'

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('approve/<int:pk>/', views.document_approve, name='document_approve'),
    path('reject/<int:pk>/', views.document_reject, name='document_reject'),
    path('create/', views.document_create, name='document_create'),
]
