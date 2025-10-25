import os
import django
import smtplib
import ssl
from email.message import EmailMessage

# --- Django setup ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()
from django.conf import settings

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ✅ Force unverified SSL context (bypass certificate validation)
ssl._create_default_https_context = ssl._create_unverified_context
context = ssl._create_unverified_context()

msg = EmailMessage()
msg["Subject"] = "Test Email — Unverified SSL"
msg["From"] = settings.DEFAULT_FROM_EMAIL
msg["To"] = "kachimaxy1@gmail.com"
msg.set_content("This is a test email sent with SSL verification disabled (for development only).")

try:
    print("Connecting to Gmail SMTP server...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        smtp.send_message(msg)
    print("✅ Email sent successfully (SSL bypassed).")
except Exception as e:
    print("❌ Failed to send email.")
    print("Error details:", e)
