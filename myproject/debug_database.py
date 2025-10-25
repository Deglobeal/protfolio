# myproject/debug_tools/debug_database.py
import os
import django
from django.db import connection
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

print("🔍 Testing Database Connection...\n")

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        print("✅ Database connection successful!")

    print("\n📦 Installed Models:")
    for model in apps.get_models():
        print(f" - {model._meta.app_label}.{model.__name__}")

except Exception as e:
    print("❌ Database connection failed.")
    print(f"Error details: {e}")
