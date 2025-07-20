# users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list, name='user_list'),  # List all users
    path('create/', views.user_create, name='user_create'),  # Create a new user
    path('edit/<int:id>/', views.user_edit, name='user_edit'),  # Edit an existing user
    path('delete/<int:id>/', views.user_delete, name='user_delete'),  # Delete a user
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
]

