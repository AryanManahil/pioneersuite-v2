from django.urls import path
from django.contrib.auth import views as auth_views
from home import views  # your app
from accounts.views import  login_view  # import your custom login view

urlpatterns = [
    # 👇 use your custom login view
    path('accounts/login/', login_view, name='login'),

    # keep Django's logout view
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # other views
    path('home/', views.home, name='home'),
]
