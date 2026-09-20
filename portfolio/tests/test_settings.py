import json
import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MANAGED_ENV_KEYS = (
    "DJANGO_DEBUG",
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "DATABASE_URL",
    "VERCEL",
    "SECURE_HSTS_SECONDS",
    "SECURE_SSL_REDIRECT",
)

DUMP_SCRIPT = """
import json
import config.settings as s
print(json.dumps({
    "DEBUG": s.DEBUG,
    "SECRET_KEY": s.SECRET_KEY,
    "ALLOWED_HOSTS": s.ALLOWED_HOSTS,
    "CSRF_TRUSTED_ORIGINS": s.CSRF_TRUSTED_ORIGINS,
    "ENGINE": s.DATABASES["default"]["ENGINE"],
    "SESSION_COOKIE_SECURE": s.SESSION_COOKIE_SECURE,
    "CSRF_COOKIE_SECURE": s.CSRF_COOKIE_SECURE,
    "SECURE_HSTS_SECONDS": s.SECURE_HSTS_SECONDS,
    "SECURE_SSL_REDIRECT": s.SECURE_SSL_REDIRECT,
    "SECURE_PROXY_SSL_HEADER": list(s.SECURE_PROXY_SSL_HEADER),
}))
"""


def load_settings(**env):
    child_env = {k: v for k, v in os.environ.items() if k not in MANAGED_ENV_KEYS}
    child_env["DJANGO_SETTINGS_MODULE"] = "config.settings"
    child_env.update(env)
    return subprocess.run(
        [sys.executable, "-c", DUMP_SCRIPT],
        env=child_env,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def settings_of(**env):
    result = load_settings(**env)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class SecretKeyAndDebugTest(SimpleTestCase):
    def test_debug_defaults_to_false(self):
        self.assertFalse(settings_of(SECRET_KEY="k" * 50)["DEBUG"])

    def test_missing_secret_key_without_debug_raises_improperly_configured(self):
        result = load_settings()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ImproperlyConfigured", result.stderr)

    def test_missing_secret_key_with_debug_uses_dev_key(self):
        conf = settings_of(DJANGO_DEBUG="1")
        self.assertTrue(conf["DEBUG"])
        self.assertTrue(conf["SECRET_KEY"])

    def test_explicit_secret_key_is_used(self):
        conf = settings_of(DJANGO_DEBUG="1", SECRET_KEY="explicit-key")
        self.assertEqual(conf["SECRET_KEY"], "explicit-key")

    def test_debug_accepts_truthy_values_case_insensitively(self):
        for value in ("1", "true", "TRUE", "Yes", "on"):
            with self.subTest(value=value):
                self.assertTrue(settings_of(DJANGO_DEBUG=value)["DEBUG"])

    def test_debug_treats_other_values_as_false(self):
        for value in ("0", "false", "no", "off", ""):
            with self.subTest(value=value):
                self.assertFalse(settings_of(DJANGO_DEBUG=value, SECRET_KEY="k" * 50)["DEBUG"])


class HostsAndOriginsTest(SimpleTestCase):
    def test_allowed_hosts_is_empty_by_default(self):
        self.assertEqual(settings_of(DJANGO_DEBUG="1")["ALLOWED_HOSTS"], [])

    def test_allowed_hosts_is_split_on_commas_and_stripped(self):
        conf = settings_of(DJANGO_DEBUG="1", ALLOWED_HOSTS=" example.com , ,localhost,")
        self.assertEqual(conf["ALLOWED_HOSTS"], ["example.com", "localhost"])

    def test_vercel_env_adds_vercel_app_suffix(self):
        conf = settings_of(DJANGO_DEBUG="1", ALLOWED_HOSTS="example.com", VERCEL="1")
        self.assertEqual(conf["ALLOWED_HOSTS"], ["example.com", ".vercel.app"])

    def test_vercel_app_suffix_is_absent_without_vercel_env(self):
        conf = settings_of(DJANGO_DEBUG="1", ALLOWED_HOSTS="example.com")
        self.assertNotIn(".vercel.app", conf["ALLOWED_HOSTS"])

    def test_csrf_trusted_origins_is_empty_by_default(self):
        self.assertEqual(settings_of(DJANGO_DEBUG="1")["CSRF_TRUSTED_ORIGINS"], [])

    def test_csrf_trusted_origins_is_split_on_commas_and_stripped(self):
        conf = settings_of(
            DJANGO_DEBUG="1",
            CSRF_TRUSTED_ORIGINS="https://example.com, https://www.example.com,",
        )
        self.assertEqual(
            conf["CSRF_TRUSTED_ORIGINS"],
            ["https://example.com", "https://www.example.com"],
        )


class DatabaseTest(SimpleTestCase):
    def test_defaults_to_sqlite(self):
        engine = settings_of(DJANGO_DEBUG="1")["ENGINE"]
        self.assertEqual(engine, "django.db.backends.sqlite3")

    def test_database_url_selects_postgresql(self):
        conf = settings_of(
            DJANGO_DEBUG="1",
            DATABASE_URL="postgres://user:pass@localhost:5432/dbname",
        )
        self.assertEqual(conf["ENGINE"], "django.db.backends.postgresql")


class ProductionSecurityTest(SimpleTestCase):
    def production(self, **env):
        return settings_of(DJANGO_DEBUG="0", SECRET_KEY="k" * 50, **env)

    def test_secure_cookies_and_proxy_header_when_debug_is_off(self):
        conf = self.production()
        self.assertTrue(conf["SESSION_COOKIE_SECURE"])
        self.assertTrue(conf["CSRF_COOKIE_SECURE"])
        self.assertEqual(conf["SECURE_PROXY_SSL_HEADER"], ["HTTP_X_FORWARDED_PROTO", "https"])

    def test_hsts_and_ssl_redirect_defaults_when_debug_is_off(self):
        conf = self.production()
        self.assertEqual(conf["SECURE_HSTS_SECONDS"], 3600)
        self.assertTrue(conf["SECURE_SSL_REDIRECT"])

    def test_hsts_and_ssl_redirect_can_be_overridden_by_env(self):
        conf = self.production(SECURE_HSTS_SECONDS="60", SECURE_SSL_REDIRECT="0")
        self.assertEqual(conf["SECURE_HSTS_SECONDS"], 60)
        self.assertFalse(conf["SECURE_SSL_REDIRECT"])

    def test_secure_flags_are_off_when_debug_is_on(self):
        conf = settings_of(DJANGO_DEBUG="1")
        self.assertFalse(conf["SESSION_COOKIE_SECURE"])
        self.assertFalse(conf["CSRF_COOKIE_SECURE"])
        self.assertEqual(conf["SECURE_HSTS_SECONDS"], 0)
        self.assertFalse(conf["SECURE_SSL_REDIRECT"])
