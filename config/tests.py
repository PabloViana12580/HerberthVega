import json
import os
import subprocess
import sys
from unittest import mock

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from config.settings import database_from_env

User = get_user_model()
PASSWORD = 'correct-Horse-battery-42'


class DatabaseConfigTests(SimpleTestCase):
    """Settings parsing only; no database connection is made."""

    def config(self, **env):
        with mock.patch.dict(os.environ, env, clear=True):
            return database_from_env()

    def test_parses_database_url_with_encoded_password(self):
        db = self.config(DATABASE_URL='postgresql://app:p%40ss%2Fword@db.example.com:5432/shop')
        self.assertEqual(db['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual((db['USER'], db['PASSWORD']), ('app', 'p@ss/word'))
        self.assertEqual((db['HOST'], db['PORT'], db['NAME']), ('db.example.com', '5432', 'shop'))

    def test_ssl_required_by_default(self):
        db = self.config(DATABASE_URL='postgresql://u:p@db.example.com:5432/postgres')
        self.assertEqual(db['OPTIONS'], {'sslmode': 'require'})

    def test_ssl_disabled_only_for_localhost(self):
        db = self.config(DATABASE_URL='postgresql://u:p@localhost:5432/shop?sslmode=disable')
        self.assertEqual(db['OPTIONS'], {'sslmode': 'disable'})
        with self.assertRaises(ImproperlyConfigured):
            self.config(DATABASE_URL='postgresql://u:p@db.example.com:5432/shop?sslmode=disable')

    def test_individual_variables(self):
        db = self.config(DB_HOST='localhost', DB_USER='u', DB_PASSWORD='p', DB_NAME='shop', DB_SSLMODE='disable')
        self.assertEqual((db['HOST'], db['NAME'], db['PORT']), ('localhost', 'shop', '5432'))

    def test_missing_configuration_is_an_error(self):
        with self.assertRaisesMessage(ImproperlyConfigured, 'DB_HOST, DB_USER, DB_PASSWORD'):
            self.config()

    def test_rejects_non_postgres_url(self):
        with self.assertRaises(ImproperlyConfigured):
            self.config(DATABASE_URL='sqlite:///db.sqlite3')


class DeploymentTests(SimpleTestCase):
    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_health_check_needs_no_login_or_https(self):
        response = self.client.get('/healthz')
        self.assertEqual((response.status_code, response.content), (200, b'ok'))
        self.assertEqual(self.client.post('/healthz').status_code, 405)
        # Other pages still redirect plain HTTP to HTTPS.
        self.assertEqual(self.client.get(reverse('login')).status_code, 301)

    def test_production_settings_need_secret_key_and_trust_render_host(self):
        """Production settings, imported in a fresh process."""
        env = {
            **os.environ,
            'DJANGO_SETTINGS_MODULE': 'config.settings',
            'DJANGO_DEBUG': 'false',
            'DJANGO_SECRET_KEY': 'test-only-secret',
            'RENDER_EXTERNAL_HOSTNAME': 'cleaning.onrender.com',
        }
        script = (
            'import json; from django.conf import settings; '
            'print(json.dumps([settings.DEBUG, settings.SESSION_COOKIE_SECURE, '
            'settings.ALLOWED_HOSTS, settings.CSRF_TRUSTED_ORIGINS]))'
        )
        output = subprocess.run([sys.executable, '-c', script], env=env, cwd=settings.BASE_DIR,
                                capture_output=True, text=True, check=True).stdout
        debug, secure_cookie, hosts, origins = json.loads(output)
        self.assertFalse(debug)
        self.assertTrue(secure_cookie)
        self.assertIn('cleaning.onrender.com', hosts)
        self.assertIn('https://cleaning.onrender.com', origins)


class RowLevelSecurityTests(TestCase):
    def test_row_level_security_enabled_on_all_public_tables(self):
        # A hosted PostgreSQL (e.g. Supabase) may expose the public schema over HTTP.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT relname, relrowsecurity FROM pg_class "
                "WHERE relnamespace = 'public'::regnamespace AND relkind = 'r'"
            )
            rls = dict(cursor.fetchall())
        self.assertIn('auth_user', rls)
        self.assertIn('catalog_service', rls)
        self.assertEqual([name for name, enabled in rls.items() if not enabled], [])


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('staff', 'staff@example.com', PASSWORD)
        self.url = reverse('login')

    def test_login_page_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'autocomplete="current-password"')
        self.assertContains(response, 'data-password-toggle')

    def test_successful_login_redirects_home(self):
        response = self.client.post(self.url, {'username': 'staff', 'password': PASSWORD})
        self.assertRedirects(response, reverse('pages:home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_wrong_password_shows_error_and_does_not_log_in(self):
        response = self.client.post(self.url, {'username': 'staff', 'password': 'wrong'})
        self.assertContains(response, 'Please enter a correct username and password')
        self.assertContains(response, 'role="alert"')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_external_next_url_is_ignored(self):
        response = self.client.post(self.url, {
            'username': 'staff', 'password': PASSWORD, 'next': 'https://evil.example.com/',
        })
        self.assertRedirects(response, reverse('pages:home'))


class LogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('staff', 'staff@example.com', PASSWORD)
        self.client.force_login(self.user)

    def test_post_logout_ends_session(self):
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('pages:home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_get_logout_is_rejected(self):
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

    def test_logout_requires_csrf_token(self):
        client = self.client_class(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(reverse('logout')).status_code, 403)


class AdminSeparationTests(TestCase):
    def test_regular_user_cannot_open_admin(self):
        self.client.force_login(User.objects.create_user('customer', 'c@example.com', PASSWORD))
        response = self.client.get(reverse('admin:index'))
        self.assertRedirects(response, f"{reverse('admin:login')}?next={reverse('admin:index')}")

    def test_administrator_can_manage_services(self):
        self.client.force_login(User.objects.create_superuser('owner', 'o@example.com', PASSWORD))
        self.assertEqual(self.client.get(reverse('admin:catalog_service_changelist')).status_code, 200)

    def test_passwords_are_hashed_and_validated(self):
        user = User.objects.create_user('staff', 'staff@example.com', PASSWORD)
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        self.assertEqual(authenticate(username='staff', password=PASSWORD), user)
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            validate_password('password')
