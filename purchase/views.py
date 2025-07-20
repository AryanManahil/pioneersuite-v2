from decimal import Decimal
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.forms.models import inlineformset_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import capfirst
from num2words import num2words
from .forms import RequisitionForm, RequisitionItemForm, PurchaseOrderForm, PurchaseOrderItemFormSet
from .models import Requisition, RequisitionItem, Vendor, PurchaseOrder, PurchaseOrderItem
from utils.pdf_utils import generate_pdf
from users.models import User



@login_required
def purchase_home(request):
    """Render the homepage of the purchase module."""
    return render(request, 'purchase/purchase_home.html')


@login_required
def requisition_list(request):
    user = request.user

    # Admins see all requisitions
    if user.groups.filter(name='Admin').exists():
        requisitions = Requisition.objects.all()

    # Managers see requisitions from their own department
    elif user.groups.filter(name='Manager').exists():
        if hasattr(user, 'department'):
            requisitions = Requisition.objects.filter(requisition_department=user.department)
        else:
            requisitions = Requisition.objects.none()

    # Normal users see only their own requisitions
    else:
        requisitions = Requisition.objects.filter(created_by=user)

    requisitions = requisitions.order_by('-id')

    # Pagination
    paginator = Paginator(requisitions, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        # 'is_dept_head': is_dept_head,
    }
    return render(request, 'purchase/requisition_list.html', context)


@login_required
@permission_required('purchase.can_approve_requisition', raise_exception=True)
def approve_requisition(request, pk):
    requisition = get_object_or_404(Requisition, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if requisition.status != 'PENDING':
            messages.error(request, "Only pending requisitions can be approved or rejected.")
            return redirect('purchase_requisition_list')  # Change to your list view name

        if action == 'approve':
            requisition.status = 'APPROVED'
            requisition.approved_by = request.user
            messages.success(request, f"Requisition {requisition} approved.")
        elif action == 'reject':
            requisition.status = 'REJECTED'
            requisition.approved_by = request.user
            messages.success(request, f"Requisition {requisition} rejected.")
        else:
            messages.error(request, "Invalid action.")

        requisition.save()
    return redirect('purchase:requisition_list')  # Change this to your actual list URL name


@login_required
def requisition_detail(request, pk):
    """Display details of a specific requisition."""
    requisition = get_object_or_404(Requisition, pk=pk)
    return render(request, 'purchase/requisition_details.html', {
        'requisition': requisition,
        'items': requisition.items.all(),
    })


@login_required
def create_requisition(request):
    ItemFormSet = inlineformset_factory(
        Requisition,
        RequisitionItem,
        form=RequisitionItemForm,
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        form = RequisitionForm(request.POST)
        requisition_instance = Requisition()  # empty instance for formset binding
        formset = ItemFormSet(request.POST, instance=requisition_instance)

        if form.is_valid() and formset.is_valid():
            requisition = form.save(commit=False)
            requisition.created_by = request.user
            requisition.requisition_department = request.user.department
            requisition.status = 'PENDING'
            requisition.save()
            formset.instance = requisition
            formset.save()
            messages.success(request, 'Requisition created successfully!')
            return redirect('purchase:requisition_list')
        else:
            messages.error(request, 'Please correct the errors in the form.')

    else:
        form = RequisitionForm(initial={'priority': 'Medium'})
        formset = ItemFormSet(instance=Requisition())

    return render(request, 'purchase/create_requisition.html', {
        'form': form,
        'formset': formset,
        'requisition_date': timezone.now().date(),
        'column_headers': ["SlNo", "Item", "Quantity", "Unit", "Note", "Delete"],
    })


@login_required
@permission_required('purchase.can_view_approved_requisition', raise_exception=True)
def purchase_requisition_list(request):
    requisitions = (
        Requisition.objects
        .filter(status__iexact='APPROVED')
        .select_related('created_by', 'requisition_department', 'approved_by')  # Use actual FK fields
        .order_by('-requisition_date')
    )
    return render(request, 'purchase/purchase_requisition_list.html', {'requisitions': requisitions})


@login_required
@permission_required('purchase.can_view_approved_requisition', raise_exception=True)
def create_purchase_order(request, requisition_id):
    requisition = get_object_or_404(Requisition, id=requisition_id)
    vendors = Vendor.objects.all()

    if request.method == "POST":
        vendor_id = request.POST.get("vendor")
        vat_percent = request.POST.get("vat_percent") or 0
        discount = request.POST.get("discount") or 0

        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            messages.error(request, "Vendor not found.")
            return redirect('purchase:create_purchase_order', requisition_id=requisition.id)

        po_number = generate_unique_po_number(requisition)

        # Create purchase order
        purchase_order = PurchaseOrder.objects.create(
            po_number=po_number,
            requisition=requisition,
            vendor=vendor,
            vat_percent=vat_percent,
            discount=discount,
            status='draft',
        )

        # Loop through requisition items
        requisition_items = requisition.items.all()
        for index, req_item in enumerate(requisition_items, start=1):
            item_name = request.POST.get(f'item_name_{index}')
            quantity = request.POST.get(f'quantity_{index}')
            unit = request.POST.get(f'unit_{index}')
            price = request.POST.get(f'price_{index}')

            # Validate item data
            if not all([item_name, quantity, unit, price]):
                messages.error(request, f"Missing data for item {index}. Purchase Order not created.")
                purchase_order.delete()
                return redirect('purchase:create_purchase_order', requisition_id=requisition.id)

            # Save item
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order,
                item_name=item_name,
                quantity=quantity,
                unit=unit,
                price=price
            )

        # Update requisition status
        requisition.status = 'done'
        requisition.save()

        messages.success(request, "✅ Purchase Order created successfully.")
        return redirect('purchase:purchase_order_list')

    return render(request, 'purchase/create_purchase_order.html', {
        'requisition': requisition,
        'vendors': vendors,
    })

@login_required
@permission_required('purchase.can_view_approved_requisition', raise_exception=True)
def purchase_order_detail(request: HttpRequest, pk: int) -> HttpResponse:
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    items = purchase_order.items.all()

    # Use Decimal for accuracy
    grand_total = sum(Decimal(item.quantity) * item.price for item in items)

    # Get VAT and Discount from PurchaseOrder model
    vat_percent = purchase_order.vat_percent or Decimal('0.0')
    discount = purchase_order.discount or Decimal('0.00')

    vat_amount = (grand_total * vat_percent) / Decimal('100')
    net_payable = grand_total + vat_amount - discount

    amount_in_words = capfirst(
        num2words(net_payable, to='currency', lang='en_IN')
        .replace('euro', 'Taka')
        .replace('cents', 'Poisha')
    )

    context = {
        'purchase_order': purchase_order,
        'items': items,
        'grand_total': grand_total,
        'vat_percent': vat_percent,
        'vat_amount': vat_amount,
        'discount': discount,
        'net_payable': net_payable,
        'amount_in_words': amount_in_words,
    }

    return render(request, 'purchase/purchase_order_details.html', context)

import datetime
# @login_required
# @permission_required('purchase.can_view_approved_requisition', raise_exception=True)

def generate_unique_po_number(requisition):
    today_str = datetime.date.today().strftime('%Y%m%d')
    base_number = f"PO-{today_str}-{requisition.id:04d}"

    # If by some rare case it's already used, increment a suffix
    counter = 1
    po_number = base_number
    while PurchaseOrder.objects.filter(po_number=po_number).exists():
        po_number = f"{base_number}-{counter}"
        counter += 1

    return po_number


@login_required
@permission_required('purchase.can_view_purchaseorder', raise_exception=True)
def purchase_order_list(request):
    vendor_filter = request.GET.get('vendor')
    status_filter = request.GET.get('status')

    orders = PurchaseOrder.objects.select_related('vendor', 'requisition')

    if vendor_filter:
        orders = orders.filter(vendor__id=vendor_filter)

    if status_filter:
        orders = orders.filter(status=status_filter)

    orders = orders.order_by('-id')  # or use 'order_date' if available

    vendors = Vendor.objects.all()

    return render(request, 'purchase/purchase_order_list.html', {
        'orders': orders,
        'vendors': vendors
    })


@login_required
@permission_required('purchase.can_view_purchaseorder', raise_exception=True)
def purchase_order_submit(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    order.status = 'submitted'
    order.save()
    messages.success(request, 'Purchase Order submitted.')
    return redirect('purchase:purchase_order_list')

def purchase_order_approve(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    order.status = 'approved'
    order.save()
    messages.success(request, 'Purchase Order approved.')
    return redirect('purchase:purchase_order_list')

def purchase_order_reject(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    order.status = 'rejected'
    order.save()
    messages.success(request, 'Purchase Order rejected.')
    return redirect('purchase:purchase_order_list')

# views.py or purchase/views.py
# from utils.pdf_utils import generate_pdf
# from .models import PurchaseOrder
#
#
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm
# from reportlab.lib import colors
#
# def draw_purchase_order(canvas_obj, purchase_order):
#     canvas_obj.setTitle(f"Purchase Order #{purchase_order.id}")
#     width, height = A4
#     margin = 2 * cm
#     y = height - margin
#
#     # Header
#     canvas_obj.setFont("Helvetica-Bold", 18)
#     canvas_obj.drawCentredString(width / 2, y, "Purchase Order")
#     y -= 1.5 * cm
#
#     # Order Info
#     canvas_obj.setFont("Helvetica", 12)
#     canvas_obj.drawString(margin, y, f"PO Number: {purchase_order.po_number}")
#     canvas_obj.drawString(width / 2, y, f"Date: {purchase_order.order_date.strftime('%d %b %Y')}")
#     y -= 0.8 * cm
#     canvas_obj.drawString(margin, y, f"Vendor: {purchase_order.vendor.name}")
#     y -= 1.2 * cm
#
#     # Table headers
#     canvas_obj.setFont("Helvetica-Bold", 12)
#     canvas_obj.drawString(margin, y, "Item Name")
#     canvas_obj.drawString(margin + 8 * cm, y, "Quantity")
#     canvas_obj.drawString(margin + 11 * cm, y, "Unit")
#     canvas_obj.drawString(margin + 14 * cm, y, "Unit Price")
#     canvas_obj.drawString(margin + 17 * cm, y, "Total")
#     y -= 0.5 * cm
#     canvas_obj.line(margin, y, width - margin, y)
#     y -= 0.5 * cm
#
#     # Table rows
#     canvas_obj.setFont("Helvetica", 11)
#     for item in purchase_order.items.all():
#         canvas_obj.drawString(margin, y, item.item_name)
#         canvas_obj.drawRightString(margin + 10.5 * cm, y, str(item.quantity))
#         canvas_obj.drawString(margin + 11 * cm, y, item.unit)
#         canvas_obj.drawRightString(margin + 16.5 * cm, y, f"৳ {item.price:.2f}")
#         total = item.quantity * item.price
#         canvas_obj.drawRightString(margin + 20 * cm, y, f"৳ {total:.2f}")
#         y -= 0.6 * cm
#         if y < margin + 4 * cm:
#             canvas_obj.showPage()
#             y = height - margin
#
#     # Totals
#     y -= 1 * cm
#     canvas_obj.setFont("Helvetica-Bold", 12)
#     canvas_obj.drawRightString(margin + 16.5 * cm, y, "Grand Total:")
#     canvas_obj.drawRightString(margin + 20 * cm, y, f"৳ {purchase_order.get_grand_total():.2f}")
#
#     y -= 0.6 * cm
#     canvas_obj.drawRightString(margin + 16.5 * cm, y, f"VAT ({purchase_order.vat_percent}%):")
#     canvas_obj.drawRightString(margin + 20 * cm, y, f"৳ {purchase_order.get_vat_amount():.2f}")
#
#     y -= 0.6 * cm
#     canvas_obj.drawRightString(margin + 16.5 * cm, y, "Discount:")
#     canvas_obj.drawRightString(margin + 20 * cm, y, f"৳ {purchase_order.discount:.2f}")
#
#     y -= 0.8 * cm
#     canvas_obj.setFont("Helvetica-Bold", 13)
#     canvas_obj.setFillColor(colors.darkgreen)
#     canvas_obj.drawRightString(margin + 16.5 * cm, y, "Net Payable:")
#     canvas_obj.drawRightString(margin + 20 * cm, y, f"৳ {purchase_order.get_net_payable():.2f}")
#     canvas_obj.setFillColor(colors.black)
#
#     # Footer
#     y -= 2 * cm
#     canvas_obj.setFont("Helvetica-Oblique", 10)
#     canvas_obj.drawString(margin, y, f"Generated by PioneerSuite")

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

def draw_purchase_order(canvas_obj, purchase_order):
    canvas_obj.setTitle(f"Purchase Order #{purchase_order.id}")
    width, height = A4
    margin = 2 * cm
    y = height - margin

    # Header
    canvas_obj.setFont("Helvetica-Bold", 18)
    canvas_obj.drawCentredString(width / 2, y, "PURCHASE ORDER")
    y -= 1.5 * cm

    # Order Info
    canvas_obj.setFont("Helvetica-Bold", 11)
    canvas_obj.drawString(margin, y, "PO Number:")
    canvas_obj.setFont("Helvetica", 11)
    canvas_obj.drawString(margin + 3.5 * cm, y, purchase_order.po_number)
    y -= 0.6 * cm

    canvas_obj.setFont("Helvetica-Bold", 11)
    canvas_obj.drawString(margin, y, "Date:")
    canvas_obj.setFont("Helvetica", 11)
    canvas_obj.drawString(margin + 3.5 * cm, y, purchase_order.order_date.strftime('%d %b %Y'))
    y -= 0.6 * cm

    canvas_obj.setFont("Helvetica-Bold", 11)
    canvas_obj.drawString(margin, y, "Vendor:")
    canvas_obj.setFont("Helvetica", 11)
    canvas_obj.drawString(margin + 3.5 * cm, y, purchase_order.vendor.name)
    y -= 1.2 * cm

    # Details
    row_height = 0.8 * cm
    table_top = y
    table_bottom = y - row_height
    table_width = width - 2 * margin

    canvas_obj.setFillColor(colors.lightblue)  # <- Change column color
    canvas_obj.rect(margin, table_bottom, table_width, row_height, stroke=1, fill=1)
    canvas_obj.setFillColor(colors.black)

    col_positions = [margin, margin + 8.5 * cm, margin + 11 * cm, margin + 13.5 * cm, margin + 17.5 * cm, margin + table_width]

    canvas_obj.setFont("Helvetica-Bold", 11)
    y = table_bottom + 0.25 * cm
    canvas_obj.drawString(margin + 0.2 * cm, y, "Item Name")
    canvas_obj.drawString(col_positions[1] + 0.2 * cm, y, "Quantity")
    canvas_obj.drawString(col_positions[2] + 0.2 * cm, y, "Unit")
    canvas_obj.drawString(col_positions[3] + 0.2 * cm, y, "Unit Price")
    canvas_obj.drawString(col_positions[4] + 0.2 * cm, y, "Total")
    y = table_bottom - 0.5 * cm

    # Table Rows
    canvas_obj.setFont("Helvetica", 10)
    for item in purchase_order.items.all():
        total = item.quantity * item.price
        canvas_obj.drawString(margin + 0.2 * cm, y, item.item_name)
        canvas_obj.drawString(col_positions[1] + 0.2 * cm, y, str(item.quantity))
        canvas_obj.drawString(col_positions[2] + 0.2 * cm, y, item.unit)
        canvas_obj.drawString(col_positions[3] + 0.2 * cm, y, f"{item.price:.2f} Taka")
        canvas_obj.drawString(col_positions[4] + 0.2 * cm, y, f"{total:.2f} Taka")
        y -= 0.6 * cm

        if y < margin + 6 * cm:
            canvas_obj.showPage()
            y = height - margin

    # Draw horizontal line after items
    canvas_obj.setLineWidth(1)
    canvas_obj.line(margin, y + 0.3 * cm, width - margin, y + 0.3 * cm)

    # Totals Section (outside the table block)
    y -= 1 * cm
    canvas_obj.setFont("Helvetica-Bold", 11)

    def draw_total_block(label, value):
        nonlocal y
        canvas_obj.drawString(margin, y, label)
        canvas_obj.setFont("Helvetica", 11)
        canvas_obj.drawString(margin + 5 * cm, y, f"{value:.2f} Taka")
        canvas_obj.setFont("Helvetica-Bold", 11)
        y -= 0.6 * cm

    draw_total_block("Grand Total", purchase_order.get_grand_total())
    draw_total_block(f"VAT ({purchase_order.vat_percent}%)", purchase_order.get_vat_amount())
    draw_total_block("Discount", purchase_order.discount)

    canvas_obj.setFont("Helvetica-Bold", 12)
    canvas_obj.setFillColor(colors.darkgreen)
    canvas_obj.drawString(margin, y, "Net Payable")
    canvas_obj.setFont("Helvetica", 12)
    canvas_obj.drawString(margin + 5 * cm, y, f"{purchase_order.get_net_payable():.2f} Taka")
    canvas_obj.setFillColor(colors.black)

    # Signature section near page footer
    sig_y = 2.5 * cm
    canvas_obj.setFont("Helvetica-Bold", 10)
    canvas_obj.drawCentredString(width / 4, sig_y + 1.5 * cm, "Prepared By:")
    canvas_obj.drawCentredString((3 * width) / 4, sig_y + 1.5 * cm, "Approved By:")

    canvas_obj.setFont("Helvetica", 10)
    canvas_obj.drawCentredString(width / 4, sig_y, "__________________________")
    canvas_obj.drawCentredString((3 * width) / 4, sig_y, "__________________________")

    # Footer
    canvas_obj.setFont("Helvetica-Oblique", 9)
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.drawString(margin, 1.2 * cm, "Generated by PioneerSuite")
    canvas_obj.setFillColor(colors.black)


@login_required
@permission_required('purchase.can_approve_requisition', raise_exception=True)
def export_purchase_order_pdf(request, pk):
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    return generate_pdf(f'purchase_order_{pk}.pdf', draw_purchase_order, purchase_order)


def some_view(request):
    print(request.user.get_all_permissions())  # Debug
