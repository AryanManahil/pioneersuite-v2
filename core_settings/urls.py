from django.urls import path
from . import views

app_name = 'core_settings'

urlpatterns = [
    # Core Settings Home
    path('', views.settings_home, name='settings_home'),

    # Company, Branch, Department Management
    path('companies/', views.company_list, name='company_list'),
    path('branches/', views.branch_list, name='branch_list'),
    path('departments/', views.department_list, name='department_list'),

    # Product / Inventory Management
    path('products/', views.product_list, name='product_list'),
]
