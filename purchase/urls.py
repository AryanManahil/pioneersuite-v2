from django.urls import path
from . import views

urlpatterns = [
    path('', views.purchase_home, name='purchase_home'),

    # Requisition for users
    path('requisitions/', views.requisition_list, name='requisition_list'),
    path('requisitions/create/', views.create_requisition, name='create_requisition'),
    path('requisitions/<int:pk>/', views.requisition_detail, name='requisition_detail'),
    path('requisitions/<int:pk>/approve/', views.approve_requisition, name='approve_requisition'),
    # Approved requisitions for Purchase Head
    path('approved-requisitions/', views.purchase_requisition_list, name='purchase_requisition_list'),
    path('create-purchase-order/', views.create_purchase_order, name='create_purchase_order'),
    # purchase/urls.py
    path('purchase-order/create/<int:requisition_id>/', views.create_purchase_order, name='create_purchase_order'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_details'),
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),

    path('purchase-order/submit/<int:pk>/', views.purchase_order_submit, name='purchase_order_submit'),
    path('purchase-order/approve/<int:pk>/', views.purchase_order_approve, name='purchase_order_approve'),
    path('purchase-order/reject/<int:pk>/', views.purchase_order_reject, name='purchase_order_reject'),
    path('purchase-order/<int:pk>/pdf/', views.export_purchase_order_pdf, name='purchase_order_pdf'),
]

