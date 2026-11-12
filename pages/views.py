from django.shortcuts import render
from django.views.decorators.http import require_GET

from catalog.models import Service

# The service whose checklist the home page hero shows.
FEATURED_SERVICE_SLUG = 'standard-clean'


@require_GET
def home(request):
    services = list(Service.objects.filter(is_active=True))
    featured = next((s for s in services if s.slug == FEATURED_SERVICE_SLUG), services[0] if services else None)
    return render(request, 'pages/home.html', {'services': services, 'featured': featured})
