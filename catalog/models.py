import uuid

from django.db import models
from django.db.models import Q
from django.urls import reverse


class Service(models.Model):
    """A cleaning service customers can browse now and book later."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    summary = models.CharField(max_length=200, help_text='One sentence shown on service cards.')
    description = models.TextField()
    includes = models.TextField(blank=True, help_text='What the visit covers, one item per line.')
    # Empty until the owner sets prices; pages then show "Price on request".
    price_from = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(
        null=True, blank=True, help_text='Typical length of a visit for an average home.',
    )
    image = models.CharField(
        max_length=120, blank=True, help_text='Static file path, e.g. img/deep-clean.jpg.',
    )
    image_alt = models.CharField(max_length=160, blank=True)
    is_active = models.BooleanField(default=True, help_text='Inactive services are hidden from the site.')
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        constraints = [
            models.CheckConstraint(
                condition=Q(price_from__isnull=True) | Q(price_from__gte=0),
                name='service_price_from_not_negative',
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:service_detail', args=[self.slug])

    @property
    def includes_list(self):
        return [line.strip() for line in self.includes.splitlines() if line.strip()]

    @property
    def duration_display(self):
        if not self.duration_minutes:
            return ''
        hours, minutes = divmod(self.duration_minutes, 60)
        if not hours:
            return f'{minutes} min'
        return f'{hours} h {minutes} min' if minutes else f'{hours} h'
