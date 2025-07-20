from django.contrib import admin
from .models import Requisition, RequisitionItem,Vendor,PurchaseOrder,PurchaseOrderItem

@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'requisition_date', 'expected_date', 'priority',"status")

@admin.register(RequisitionItem)
class RequisitionItemAdmin(admin.ModelAdmin):
    list_display = ('requisition', 'item_name', 'quantity', 'unit')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'email')
    search_fields = ('name', 'contact', 'email')

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'requisition', 'vendor', 'order_date', 'status')
    list_filter = ('status', 'order_date')
    search_fields = ('po_number',)

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'purchase_order', 'quantity', 'unit', 'price')
    search_fields = ('item_name',)

