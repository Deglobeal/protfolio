# myapp/middleware.py
import time
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware:
    """
    Add security headers to all responses
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (CSP) - Adjust based on your needs
        csp = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com",
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com",
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
            "img-src 'self' data: https:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response['Content-Security-Policy'] = '; '.join(csp)
        
        return response

class ContentProtectionMiddleware:
    """
    Middleware to add content protection headers and prevent hotlinking
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add headers to help with content protection
        response['X-Content-Protection'] = 'enabled'
        response['X-Download-Options'] = 'noopen'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        return response

class AntiScrapingMiddleware:
    """
    Basic anti-scraping protection
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_times = {}

    def __call__(self, request):
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Rate limiting for same IP
        if client_ip in self.request_times:
            last_request_time = self.request_times[client_ip]
            if current_time - last_request_time < 0.1:  # 100ms between requests
                logger.warning(f"Rapid requests detected from IP: {client_ip}")
                return HttpResponseForbidden("Too many requests")
        
        self.request_times[client_ip] = current_time
        
        # Clean old entries (prevent memory leak)
        if len(self.request_times) > 1000:
            self.clean_old_entries()
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def clean_old_entries(self):
        current_time = time.time()
        self.request_times = {ip: time for ip, time in self.request_times.items() 
                            if current_time - time < 300}  # Keep last 5 minutes

class AdminProtectionMiddleware:
    """
    Additional protection for admin routes
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            # Add extra security headers for admin
            response = self.get_response(request)
            response['X-Robots-Tag'] = 'noindex, nofollow'
            return response
        
        return self.get_response(request)

class MaintenanceModeMiddleware:
    """
    Enable maintenance mode when needed
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if maintenance mode is enabled
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Allow admin users and specific paths
            if (request.user.is_staff or 
                request.path.startswith('/admin/') or 
                request.path.startswith('/accounts/login/')):
                return self.get_response(request)
            
            # Return maintenance page for others
            from django.shortcuts import render
            return render(request, 'main/maintenance.html', status=503)
        
        return self.get_response(request)

class RequestLoggingMiddleware:
    """
    Log all requests for security monitoring
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        logger.info(f"Request: {request.method} {request.path} - IP: {self.get_client_ip(request)} - User: {request.user}")
        
        response = self.get_response(request)
        
        # Log response status
        logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
        
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip