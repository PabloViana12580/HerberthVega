from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import Service


def make_service(**overrides):
    data = {
        'name': 'Window clean',
        'slug': 'window-clean',
        'summary': 'Inside and outside glass.',
        'description': 'Glass, frames, and sills.',
        'includes': 'Inside glass\n\n  Outside glass  \nSills',
        'sort_order': 99,
    }
    data.update(overrides)
    return Service.objects.create(**data)


class ServiceModelTests(SimpleTestCase):
    """Pure model helpers; no database."""

    def test_includes_list_skips_blank_lines_and_trims(self):
        service = Service(includes='Inside glass\n\n  Outside glass  \nSills')
        self.assertEqual(service.includes_list, ['Inside glass', 'Outside glass', 'Sills'])

    def test_duration_display(self):
        self.assertEqual(Service(duration_minutes=None).duration_display, '')
        self.assertEqual(Service(duration_minutes=45).duration_display, '45 min')
        self.assertEqual(Service(duration_minutes=120).duration_display, '2 h')
        self.assertEqual(Service(duration_minutes=150).duration_display, '2 h 30 min')


class ServiceDatabaseTests(TestCase):
    def test_starter_services_are_loaded_by_migration(self):
        slugs = set(Service.objects.values_list('slug', flat=True))
        self.assertTrue({'standard-clean', 'deep-clean', 'move-in-move-out-clean'} <= slugs)
        self.assertFalse(Service.objects.exclude(price_from=None).exists(), 'prices are left for the owner')

    def test_negative_price_is_rejected_by_the_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_service(price_from=Decimal('-1'))

    def test_slug_is_unique(self):
        make_service()
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_service(name='Other name')


class ServiceViewTests(TestCase):
    def test_list_shows_active_services_only(self):
        make_service(name='Hidden clean', slug='hidden-clean', is_active=False)
        response = self.client.get(reverse('catalog:service_list'))
        self.assertContains(response, 'Deep clean')
        self.assertNotContains(response, 'Hidden clean')

    def test_detail_shows_checklist_and_price(self):
        service = make_service(price_from=Decimal('120.00'), duration_minutes=90)
        response = self.client.get(service.get_absolute_url())
        self.assertContains(response, '<h1 class="cs-page-title" id="page-title">Window clean</h1>', html=True)
        self.assertContains(response, 'Outside glass')
        self.assertContains(response, 'From $120')
        self.assertContains(response, '1 h 30 min')

    def test_detail_without_price_says_price_on_request(self):
        response = self.client.get(reverse('catalog:service_detail', args=['deep-clean']))
        self.assertContains(response, 'Price on request')

    def test_inactive_or_unknown_service_is_404(self):
        make_service(is_active=False)
        self.assertEqual(self.client.get(reverse('catalog:service_detail', args=['window-clean'])).status_code, 404)
        self.assertEqual(self.client.get(reverse('catalog:service_detail', args=['nope'])).status_code, 404)

    def test_service_text_is_escaped(self):
        service = make_service(summary='<script>alert(1)</script>')
        response = self.client.get(reverse('catalog:service_list'))
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, '&lt;script&gt;')
        self.assertEqual(self.client.post(service.get_absolute_url()).status_code, 405)
