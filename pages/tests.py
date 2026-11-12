from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.models import Service


class HomePageTests(TestCase):
    def test_home_lists_services_and_hero_checklist(self):
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/home.html')
        self.assertEqual(response.context['featured'].slug, 'standard-clean')
        self.assertContains(response, 'Every standard clean includes')
        self.assertContains(response, 'Vacuum and mop all floors')
        for service in Service.objects.filter(is_active=True):
            self.assertContains(response, service.get_absolute_url())

    @override_settings(BUSINESS_NAME='Test Cleaners', BUSINESS_PHONE='+1 (860) 555-0100')
    def test_business_details_come_from_settings(self):
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, 'Test Cleaners')
        self.assertContains(response, 'href="tel:+18605550100"')

    def test_home_without_services_invites_a_call(self):
        Service.objects.update(is_active=False)
        response = self.client.get(reverse('pages:home'))
        self.assertIsNone(response.context['featured'])
        self.assertContains(response, 'Services will be listed here soon')
        self.assertNotContains(response, 'cs-checklist__items')

    def test_staff_sign_in_link_and_sign_out_form(self):
        self.assertContains(self.client.get(reverse('pages:home')), reverse('login'))
        from django.contrib.auth import get_user_model
        self.client.force_login(get_user_model().objects.create_user('staff', 's@example.com', 'x-Pass-word-42'))
        response = self.client.get(reverse('pages:home'))
        self.assertContains(response, f'action="{reverse("logout")}"')
