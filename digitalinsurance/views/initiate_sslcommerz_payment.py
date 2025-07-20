import requests
from django.conf import settings

post_data = {
    'store_id': settings.SSLCOMMERZ_STORE_ID,
    'store_passwd': settings.SSLCOMMERZ_STORE_PASS,
'cus_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email,
    # ... other data ...
}

response = requests.post(settings.SSLCOMMERZ_INIT_URL, data=post_data)
