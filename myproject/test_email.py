import os
import django
import smtplib
import ssl
from email.message import EmailMessage

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings

# Gmail SMTP details
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# === Patch SSL for Python 3.13 ===
def patched_create_default_context(*args, **kwargs):
    ctx = ssl._create_unverified_context()
    return ctx

ssl.create_default_context = patched_create_default_context

# Prepare the test email
msg = EmailMessage()
msg["Subject"] = "Django Email Test"
msg["From"] = settings.DEFAULT_FROM_EMAIL
msg["To"] = "kachimaxy1@gmail.com"
msg.set_content("Hello! This is a Django test email sent using Gmail SMTP.")

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        smtp.send_message(msg)
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Failed to send email.")
    print("Error details:", e)
