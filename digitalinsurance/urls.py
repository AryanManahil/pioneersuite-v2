from django.urls import path

# Home & Common Views
from digitalinsurance.views import views as home_views
from digitalinsurance.views.views import digital_insurance_landing
from digitalinsurance.views.customer_views import (
    customer_dashboard,
    my_quotes_view,
    my_policies_view,
    my_payments_view,
    my_claims_view,
)
from digitalinsurance.views.customerprofile import customer_profile_view, customer_profile_edit
from digitalinsurance.views.common import dashboard_redirect

# Product & Quote Views
from digitalinsurance.views import product as product_views
from digitalinsurance.views import quote as quote_views

# Admin Views
from digitalinsurance.views.admin_dashboard import admin_dashboard
from digitalinsurance.views.customer_admin import (
    all_customer_profiles,
    admin_customer_detail,
    all_policies,
)

# Policy Detail View
from digitalinsurance.views.policy_detail import policy_detail
from digitalinsurance.views import payment
from digitalinsurance.views.quote_list import quote_list
from digitalinsurance.views.pdfs import download_policy_pdf


app_name = 'digitalinsurance'

# ... urlpatterns as before


urlpatterns = [
    # 🏠 Home & Static Pages
    path('', home_views.dihome_home, name='di_home'),
    path('policy/', home_views.policy, name='policy'),
    path('claim/', home_views.claim, name='claim'),
    path('bill/', home_views.bill, name='bill'),
    path('digital-landing/', digital_insurance_landing, name='digital_product_view'),

    # 📦 Product Management
    path('products/', product_views.product_list, name='product_list'),
    path('products/add/', product_views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', product_views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', product_views.product_delete, name='product_delete'),
    path('products/<slug:code>/', product_views.product_detail, name='product_detail'),

    # 🧾 Quotes & Travel Plans
    path('travel-quote/<int:plan_id>/', quote_views.travel_quote_view, name='travel_quote'),
    path('travel-purpose/<int:plan_id>/', quote_views.travel_purpose_detail, name='travel_purpose_detail'),
    path('quote/<int:quote_id>/ssl-pay/', payment.initiate_sslcommerz_payment, name='initiate_sslcommerz_payment'),


    # 👤 Customer Dashboard & Profile
    path('dashboard/customer/', customer_dashboard, name='customer_dashboard'),
    path('customer-profile/', customer_profile_view, name='customer_profile_view'),
    path('customer-profile/edit/', customer_profile_edit, name='customer_profile_edit'),

    # 📝 Customer Info & Quotes
    path('quotes/', my_quotes_view, name='my_quotes'),
    path('my-policies/', my_policies_view, name='my_policies'),
    path('payments/', my_payments_view, name='my_payments'),
    path('claims/', my_claims_view, name='my_claims'),

    # 🛠 Admin Views
    path('admin/customers/', all_customer_profiles, name='admin_customer_list'),
    path('admin/customers/<int:pk>/', admin_customer_detail, name='admin_customer_detail'),
    path('policies/', all_policies, name='all_policies'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),

    # 🔀 Utility
    path('dashboard/', dashboard_redirect, name='dashboard'),
    path('policy/<int:policy_id>/', policy_detail, name='policy_detail'),

    path('payment/success/', payment.sslcommerz_success, name='sslcommerz_success'),
    path('payment/fail/', payment.sslcommerz_fail, name='sslcommerz_fail'),
    path('payment/cancel/', payment.sslcommerz_cancel, name='sslcommerz_cancel'),
    path('quotes/', quote_list, name='quote_list'),
    path('policy/<int:policy_id>/download-pdf/', download_policy_pdf, name='download_policy_pdf'),
]
