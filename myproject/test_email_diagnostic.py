import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=== Email Configuration Test ===")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'Not set')}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

try:
    print("\nAttempting to send test email...")
    send_mail(
        'Test Email from Portfolio',
        'This is a test email from your portfolio site.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.EMAIL_HOST_USER],  # Send to yourself
        fail_silently=False,
    )
    print("✅ SUCCESS: Email sent successfully!")
except Exception as e:
    print(f"❌ FAILED: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # More detailed error information
    import traceback
    traceback.print_exc()