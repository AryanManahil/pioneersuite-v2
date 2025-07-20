import requests
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from digitalinsurance.models import Quote, InsurancePolicy
from digitalinsurance.utils import generate_policy_number


@login_required
def initiate_sslcommerz_payment(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id, customer=request.user)

    transaction_id = f"QUOTE{quote.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    post_data = {
        'store_id': settings.SSLCOMMERZ['STORE_ID'],
        'store_passwd': settings.SSLCOMMERZ['STORE_PASS'],
        'total_amount': quote.total_premium,
        'currency': 'BDT',
        'tran_id': transaction_id,
        'success_url': request.build_absolute_uri(reverse('digitalinsurance:sslcommerz_success')),
        'fail_url': request.build_absolute_uri(reverse('digitalinsurance:sslcommerz_fail')),
        'cancel_url': request.build_absolute_uri(reverse('digitalinsurance:sslcommerz_cancel')),
        'cus_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email,
        'cus_email': request.user.email,
        'cus_add1': 'Dhaka',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'cus_phone': '01700000000',
        'product_name': quote.product.name,
        'shipping_method': 'NO',
        'num_of_item': 1,
    }

    try:
        response = requests.post(settings.SSLCOMMERZ['INIT_URL'], data=post_data, timeout=15)
        response.raise_for_status()
        response_data = response.json()
    except requests.RequestException as e:
        return render(request, 'digitalinsurance/payment_error.html', {
            'error': f'Error initiating payment: {str(e)}'
        })

    if response_data.get('status') == 'SUCCESS':
        return redirect(response_data['GatewayPageURL'])
    else:
        return render(request, 'digitalinsurance/payment_error.html', {
            'error': response_data.get('failedreason', 'Payment initiation failed.')
        })


@csrf_exempt
def sslcommerz_success(request):
    val_id = request.POST.get('val_id')
    tran_id = request.POST.get('tran_id')

    if not val_id:
        return render(request, 'digitalinsurance/payment_error.html', {
            'error': 'Validation ID not received from SSLCommerz.'
        })

    validation_url = (
        f"{settings.SSLCOMMERZ['VALIDATION_URL']}?val_id={val_id}"
        f"&store_id={settings.SSLCOMMERZ['STORE_ID']}"
        f"&store_passwd={settings.SSLCOMMERZ['STORE_PASS']}&v=1&format=json"
    )

    try:
        validation_response = requests.get(validation_url, timeout=15)
        validation_response.raise_for_status()
        validation_data = validation_response.json()
    except requests.RequestException as e:
        return render(request, 'digitalinsurance/payment_error.html', {
            'error': f'Could not verify payment with SSLCommerz: {str(e)}'
        })

    status = validation_data.get('status')
    custom_tran_id = validation_data.get('tran_id')

    if status != 'VALID' or not custom_tran_id:
        return render(request, 'digitalinsurance/payment_error.html', {
            'error': 'Payment was not successful or not valid.'
        })

    try:
        quote_id_str = custom_tran_id.split('-')[0].replace('QUOTE', '')
        quote_id = int(quote_id_str)
        quote = get_object_or_404(Quote, id=quote_id)
    except (IndexError, ValueError):
        return render(request, 'digitalinsurance/payment_error.html', {
            'error': 'Invalid transaction or quote not found.'
        })

    if quote.status != 'approved':
        quote.status = 'approved'
        quote.save()

        departure_date = datetime.today().date()
        duration_days = 60
        end_date = departure_date + timedelta(days=duration_days)

        policy = InsurancePolicy.objects.create(
            user=quote.customer,
            product=quote.product,
            quote=quote,
            policy_number=generate_policy_number(),
            premium_amount=quote.total_premium,
            start_date=departure_date,
            end_date=end_date,
            status='ACTIVE',
            transaction_id=tran_id,
            transaction_time=timezone.now(),
            transaction_method='SSLCommerz'
        )

        return redirect('digitalinsurance:policy_detail', policy.id)

    return redirect('digitalinsurance:customer_dashboard')


@csrf_exempt
def sslcommerz_fail(request):
    return render(request, 'digitalinsurance/payment_error.html', {
        'error': 'Payment failed or was declined. Please try again.'
    })


@csrf_exempt
def sslcommerz_cancel(request):
    return render(request, 'digitalinsurance/payment_error.html', {
        'error': 'Payment was cancelled by the user.'
    })
