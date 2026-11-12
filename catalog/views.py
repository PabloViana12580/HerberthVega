from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Service


@require_GET
def service_list(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'catalog/service_list.html', {'services': services})


@require_GET
def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    others = Service.objects.filter(is_active=True).exclude(pk=service.pk)[:3]
    return render(request, 'catalog/service_detail.html', {'service': service, 'others': others})
