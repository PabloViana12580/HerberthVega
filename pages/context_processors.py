from django.conf import settings


def business(request):
    """Business name and contact details from settings, for every template."""
    return {
        'business': {
            'name': settings.BUSINESS_NAME,
            'phone': settings.BUSINESS_PHONE,
            'phone_href': 'tel:' + ''.join(ch for ch in settings.BUSINESS_PHONE if ch.isdigit() or ch == '+'),
            'email': settings.BUSINESS_EMAIL,
            'service_area': settings.BUSINESS_SERVICE_AREA,
            'hours': settings.BUSINESS_HOURS,
        },
    }
