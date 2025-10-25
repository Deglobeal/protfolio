"""
Comprehensive Django Deployment Test Script
Tests all critical areas of your project for production readiness.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

import importlib
from django.conf import settings
from django.core import mail
from django.db import connection, DatabaseError
from django.test import Client, TestCase
from django.urls import reverse, NoReverseMatch
from django.core.management import call_command
from django.contrib.auth.models import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DeploymentTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        
    def log_success(self, message):
        logger.info(f"✅ {message}")
        self.success_count += 1
        
    def log_warning(self, message):
        logger.warning(f"⚠️  {message}")
        self.warnings.append(message)
        
    def log_error(self, message):
        logger.error(f"❌ {message}")
        self.errors.append(message)
        
    def run_all_tests(self):
        """Run all deployment tests"""
        print("=" * 60)
        print("🚀 DJANGO DEPLOYMENT READINESS TEST")
        print("=" * 60)
        
        tests = [
            self.test_environment,
            self.test_database,
            self.test_static_files,
            self.test_media_files,
            self.test_email_config,
            self.test_urls,
            self.test_models,
            self.test_middleware,
            self.test_admin,
            self.test_templates,
            self.test_security,
            self.test_dependencies,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_error(f"Test {test.__name__} crashed: {str(e)}")
        
        self.generate_report()
    
    def test_environment(self):
        """Test environment and basic settings"""
        logger.info("\n🔧 Testing Environment & Settings...")
        
        # Check DEBUG mode
        if settings.DEBUG:
            self.log_warning("DEBUG mode is enabled - Disable in production!")
        else:
            self.log_success("DEBUG mode is disabled (good for production)")
        
        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS:
            self.log_error("ALLOWED_HOSTS is empty!")
        else:
            self.log_success(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # Check SECRET_KEY
        if settings.SECRET_KEY.startswith('django-insecure-'):
            self.log_error("Using default SECRET_KEY - Change in production!")
        else:
            self.log_success("SECRET_KEY is set")
        
        # Check database
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite3' in db_engine:
            self.log_warning("Using SQLite - Consider PostgreSQL for production")
        else:
            self.log_success(f"Using {db_engine} database")
    
    def test_database(self):
        """Test database connectivity and models"""
        logger.info("\n🗄️  Testing Database...")
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.log_success("Database connection successful")
        except DatabaseError as e:
            self.log_error(f"Database connection failed: {e}")
            return
        
        # Test model imports and basic queries
        try:
            from myapp.models import Project, Certificate, ContactMessage
            
            # Test Project model
            project_count = Project.objects.count()
            self.log_success(f"Project model: {project_count} records")
            
            # Test Certificate model
            certificate_count = Certificate.objects.count()
            self.log_success(f"Certificate model: {certificate_count} records")
            
            # Test ContactMessage model
            contact_count = ContactMessage.objects.count()
            self.log_success(f"ContactMessage model: {contact_count} records")
            
        except Exception as e:
            self.log_error(f"Model test failed: {e}")
    
    def test_static_files(self):
        """Test static files configuration"""
        logger.info("\n📁 Testing Static Files...")
        
        # Check static directories
        static_dirs = [
            settings.STATIC_ROOT,
            *[str(path) for path in settings.STATICFILES_DIRS]
        ]
        
        for static_dir in static_dirs:
            if os.path.exists(static_dir):
                self.log_success(f"Static directory exists: {static_dir}")
            else:
                self.log_warning(f"Static directory missing: {static_dir}")
        
        # Test collectstatic
        try:
            static_root = settings.STATIC_ROOT
            if static_root and os.path.exists(static_root):
                static_files = len([f for f in Path(static_root).rglob('*') if f.is_file()])
                self.log_success(f"Static files collected: {static_files} files")
            else:
                self.log_warning("Run 'python manage.py collectstatic' before deployment")
        except Exception as e:
            self.log_error(f"Static files check failed: {e}")
    
    def test_media_files(self):
        """Test media files configuration"""
        logger.info("\n🖼️  Testing Media Files...")
        
        media_root = settings.MEDIA_ROOT
        if media_root and os.path.exists(media_root):
            self.log_success(f"Media directory exists: {media_root}")
        else:
            self.log_warning(f"Media directory missing: {media_root}")
    
    def test_email_config(self):
        """Test email configuration"""
        logger.info("\n📧 Testing Email Configuration...")
        
        email_backend = settings.EMAIL_BACKEND
        
        if 'console' in email_backend or 'file' in email_backend:
            self.log_warning(f"Using {email_backend} - Configure real email for production")
        else:
            self.log_success(f"Email backend: {email_backend}")
        
        # Test email settings
        required_email_settings = ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER']
        for setting in required_email_settings:
            if hasattr(settings, setting) and getattr(settings, setting):
                self.log_success(f"{setting} is configured")
            else:
                self.log_warning(f"{setting} is not configured")
        
        # Test email connection (without actually sending)
        try:
            connection = mail.get_connection()
            connection.open()
            connection.close()
            self.log_success("Email connection test passed")
        except Exception as e:
            self.log_warning(f"Email connection test: {e}")
    
    def test_urls(self):
        """Test URL configuration"""
        logger.info("\n🌐 Testing URLs...")
        
        client = Client()
        
        # Test critical URLs
        critical_urls = [
            ('home', '/'),
            ('projects', '/projects/'),
            ('contact', '/contact/'),
            ('skills', '/skills/'),
            ('certificates', '/certificates/'),
            ('admin:index', '/admin/'),
        ]
        
        for name, url in critical_urls:
            try:
                if name == 'admin:index':
                    response = client.get(url, follow=True)
                    expected_status = 200  # Should redirect to login
                else:
                    response = client.get(url)
                    expected_status = 200
                
                if response.status_code == expected_status:
                    self.log_success(f"URL {url} - Status {response.status_code}")
                else:
                    self.log_warning(f"URL {url} - Unexpected status {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"URL {url} - Error: {e}")
    
    def test_models(self):
        """Test all models can be imported and have required fields"""
        logger.info("\n📊 Testing Models...")
        
        try:
            # Import all models from your app
            from myapp import models
            
            for model_name in dir(models):
                model_class = getattr(models, model_name)
                if isinstance(model_class, type) and hasattr(model_class, '_meta'):
                    try:
                        # Try to create a minimal instance if possible
                        instance = model_class()
                        self.log_success(f"Model {model_name} - OK")
                    except Exception as e:
                        self.log_warning(f"Model {model_name} - Issue: {e}")
                        
        except Exception as e:
            self.log_error(f"Models test failed: {e}")
    
    def test_middleware(self):
        """Test middleware configuration"""
        logger.info("\n🛡️  Testing Middleware...")
        
        for middleware in settings.MIDDLEWARE:
            try:
                # Try to import the middleware class
                module_path, class_name = middleware.rsplit('.', 1)
                module = importlib.import_module(module_path)
                middleware_class = getattr(module, class_name)
                self.log_success(f"Middleware {class_name} - OK")
            except Exception as e:
                self.log_error(f"Middleware {middleware} - Import failed: {e}")
    
    def test_admin(self):
        """Test admin site"""
        logger.info("\n⚙️  Testing Admin Site...")
        
        try:
            # Check if admin is accessible
            client = Client()
            response = client.get('/admin/', follow=True)
            
            if response.status_code == 200:
                self.log_success("Admin site accessible")
            else:
                self.log_warning(f"Admin site returned status {response.status_code}")
                
            # Check if superuser exists
            superusers = User.objects.filter(is_superuser=True)
            if superusers.exists():
                self.log_success(f"Superuser exists: {superusers.count()} accounts")
            else:
                self.log_warning("No superuser found - Create one with 'python manage.py createsuperuser'")
                
        except Exception as e:
            self.log_error(f"Admin test failed: {e}")
    
    def test_templates(self):
        """Test template configuration"""
        logger.info("\n📄 Testing Templates...")
        
        # Check template directories
        for template_config in settings.TEMPLATES:
            if 'DIRS' in template_config:
                for template_dir in template_config['DIRS']:
                    if os.path.exists(template_dir):
                        self.log_success(f"Template directory exists: {template_dir}")
                    else:
                        self.log_warning(f"Template directory missing: {template_dir}")
    
    def test_security(self):
        """Test security settings"""
        logger.info("\n🔒 Testing Security Settings...")
        
        security_checks = [
            ('DEBUG', False, "DEBUG should be False in production"),
            ('SECURE_SSL_REDIRECT', True, "SSL redirect should be enabled"),
            ('SESSION_COOKIE_SECURE', True, "Secure session cookies"),
            ('CSRF_COOKIE_SECURE', True, "Secure CSRF cookies"),
            ('SECURE_BROWSER_XSS_FILTER', True, "XSS filter enabled"),
            ('SECURE_CONTENT_TYPE_NOSNIFF', True, "Content type nosniff"),
            ('X_FRAME_OPTIONS', 'DENY', "Clickjacking protection"),
        ]
        
        for setting, expected_value, description in security_checks:
            actual_value = getattr(settings, setting, None)
            if actual_value == expected_value:
                self.log_success(f"{setting}: {description}")
            else:
                self.log_warning(f"{setting}: {description} (current: {actual_value})")
    
    def test_dependencies(self):
        """Test required dependencies"""
        logger.info("\n📦 Testing Dependencies...")
        
        required_packages = [
            'Django',
            'Pillow',  # For ImageField
            'whitenoise',  # For static files
            'gunicorn',  # For production server
        ]
        
        for package in required_packages:
            try:
                importlib.import_module(package.lower().replace('-', '_'))
                self.log_success(f"{package} - Installed")
            except ImportError:
                self.log_warning(f"{package} - Not installed")
    
    def generate_report(self):
        """Generate final deployment report"""
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT TEST REPORT")
        print("=" * 60)
        
        print(f"\n✅ Successes: {self.success_count}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.errors:
            print("\n❌ ERRORS (must fix before deployment):")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("\n🎉 No critical errors found!")
        
        if not self.errors and not self.warnings:
            print("\n🚀 Your project is ready for deployment!")
        elif not self.errors:
            print("\n📝 Project has warnings but can be deployed (review warnings)")
        else:
            print("\n🛑 Fix errors before deployment!")
        
        print("\n" + "=" * 60)

def main():
    """Main function to run deployment tests"""
    tester = DeploymentTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()