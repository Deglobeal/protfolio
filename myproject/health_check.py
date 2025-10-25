"""
Quick Health Check for Django Project
Run this daily to ensure everything is working.
"""

import os
import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from django.db import connection
from django.core.management import call_command
from myapp.models import ContactMessage, Project, Certificate

def quick_health_check():
    print("🔍 Quick Health Check")
    print("=" * 40)
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database: OK")
    except Exception as e:
        print(f"❌ Database: {e}")
        return
    
    # Model counts
    try:
        projects = Project.objects.count()
        certificates = Certificate.objects.count()
        messages = ContactMessage.objects.count()
        
        print(f"✅ Projects: {projects}")
        print(f"✅ Certificates: {certificates}") 
        print(f"✅ Contact Messages: {messages}")
        
    except Exception as e:
        print(f"❌ Models: {e}")
    
    # Recent activity
    try:
        recent_messages = ContactMessage.objects.order_by('-created_at')[:3]
        if recent_messages:
            print(f"✅ Recent messages: {len(recent_messages)}")
        else:
            print("ℹ️  No recent messages")
    except Exception as e:
        print(f"❌ Recent activity: {e}")
    
    print("=" * 40)
    print("✅ Health Check Complete")

if __name__ == "__main__":
    quick_health_check()