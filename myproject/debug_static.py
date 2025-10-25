# myproject/debug_tools/debug_static.py
import os
from django.conf import settings
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

print("🔍 Checking static files...\n")
static_dir = Path(settings.STATIC_ROOT)

if not static_dir.exists():
    print("❌ STATIC_ROOT directory not found.")
else:
    files = list(static_dir.rglob('*'))
    print(f"✅ Found {len(files)} static files in {static_dir}")
    if not files:
        print("⚠️ Static directory is empty — did you run collectstatic?")
