from .models import Service


def nav_services(request):
    """Active services for the header menu and footer; evaluated only if a template uses them."""
    return {'nav_services': Service.objects.filter(is_active=True).only('name', 'slug')}
