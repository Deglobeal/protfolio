# myproject/debug_tools/debug_security.py
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

print("🔍 Checking Django Security Settings...\n")

checks = {
    "DEBUG": not settings.DEBUG,
    "SECRET_KEY": settings.SECRET_KEY != "django-insecure-please-change-me",
    "ALLOWED_HOSTS": bool(settings.ALLOWED_HOSTS),
    "SECURE_SSL_REDIRECT": getattr(settings, "SECURE_SSL_REDIRECT", False),
    "CSRF_COOKIE_SECURE": getattr(settings, "CSRF_COOKIE_SECURE", False),
    "SESSION_COOKIE_SECURE": getattr(settings, "SESSION_COOKIE_SECURE", False),
}

for key, passed in checks.items():
    status = "✅ OK" if passed else "❌ FAIL"
    print(f"{status} {key}")

print("\n💡 Tip: All values should be ✅ for production.")
