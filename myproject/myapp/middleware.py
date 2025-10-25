# myapp/middleware.py
import re, io
import requests  # Add this import at the top
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils.html import escape
from django.conf import settings
from django.http import HttpResponseForbidden
from collections import defaultdict # For tracking requests per IP
from django.utils import timezone
from django.utils import timezone
from reportlab.lib.pagesizes import letter


logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy (CSP)
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
        response['X-Content-Protection'] = 'enabled'
        response['X-Download-Options'] = 'noopen'
        response['X-Content-Type-Options'] = 'nosniff'
        return response


class AntiScrapingMiddleware:
    """
    Smarter anti-scraping protection.
    Allows normal browsing but blocks excessive rapid requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Store request timestamps per IP
        self.requests = defaultdict(list)

    def __call__(self, request):
        client_ip = self.get_client_ip(request)
        now = time.time()

        # ✅ Allow admin, static, and media files to bypass
        if request.path.startswith(("/admin/", "/static/", "/media/")):
            return self.get_response(request)

        # Keep only requests in the last 10 seconds
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < 10]
        self.requests[client_ip].append(now)

        # 🚨 If more than 50 requests in 10 seconds, block it
        if len(self.requests[client_ip]) > 50:
            logger.warning(f"Blocked scraping attempt from IP {client_ip} "
                           f"({len(self.requests[client_ip])} requests in 10s)")
            return HttpResponseForbidden("Too many requests")

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')



class AdminProtectionMiddleware:
    """
    Extra protection for /admin/
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            response = self.get_response(request)
            response['X-Robots-Tag'] = 'noindex, nofollow'
            return response
        return self.get_response(request)


class MaintenanceModeMiddleware:
    """
    Maintenance mode support
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            if (request.user.is_staff or
                request.path.startswith('/admin/') or
                request.path.startswith('/accounts/login/')):
                return self.get_response(request)

            from django.shortcuts import render
            return render(request, 'main/maintenance.html', status=503)

        return self.get_response(request)


class RequestLoggingMiddleware:
    """
    Logs all requests
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info(f"Request: {request.method} {request.path} - IP: {self.get_client_ip(request)} - User: {request.user}")
        response = self.get_response(request)
        logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


import json
import logging
import re
import requests
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class WatermarkMiddleware(MiddlewareMixin):
    """
    Enhanced Watermark Middleware
    - Works on both desktop and mobile devices
    - Detects suspicious activity (print, dev tools, tab switch)
    - Uses hybrid geolocation (IP + Browser GPS)
    - Logs screenshot or suspicious attempts server-side
    """

    def process_response(self, request, response):
        # Apply only to HTML responses
        if not response.get("Content-Type", "").startswith("text/html"):
            return response

        # Limit to specific paths (customize this list)
        protected_paths = [r"^/$", r"^/portfolio/?$", r"^/projects/?$", r"^/about/?$"]

        for pattern in protected_paths:
            if re.match(pattern, request.path):
                try:
                    client_ip = self.get_client_ip(request)
                    location_data = self.get_location_data(client_ip)
                    response.content = self.inject_watermark_html(response, location_data)
                except Exception as e:
                    logger.error(f"Watermark injection failed: {e}")
                break
        return response

    # ---------------------------
    # Helper: Get client IP
    # ---------------------------
    def get_client_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        return forwarded.split(",")[0] if forwarded else request.META.get("REMOTE_ADDR", "0.0.0.0")

    # ---------------------------
    # Helper: Get IP-based location
    # ---------------------------
    def get_location_data(self, ip):
        try:
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
            data = response.json()
            return {
                "ip": ip,
                "city": data.get("city", "Unknown"),
                "region": data.get("region", ""),
                "country": data.get("country", ""),
                "loc": data.get("loc", ""),
            }
        except Exception as e:
            logger.warning(f"IP lookup failed: {e}")
            return {"ip": ip, "city": "Unknown", "region": "", "country": "", "loc": ""}

    # ---------------------------
    # Helper: Inject HTML + JS
    # ---------------------------
    def inject_watermark_html(self, response, location_data):
        watermark_html = f"""
        <div id="__watermark_overlay"
            style="
                position:fixed;
                top:0;
                left:0;
                width:100%;
                height:100%;
                background:rgba(0,0,0,0.7);
                color:white;
                display:none;
                z-index:9999;
                font-size:1.5rem;
                justify-content:center;
                align-items:center;
                text-align:center;
                font-family:Arial, sans-serif;">
            ⚠ Unauthorized Action Detected!<br>
            Logged from IP: {location_data.get('ip')}<br>
            {location_data.get('city')}, {location_data.get('country')}
        </div>

        <script>
        (function() {{
            const overlay = document.getElementById('__watermark_overlay');

            // Function to show warning overlay
            const showWatermark = (reason) => {{
                overlay.style.display = 'flex';
                console.warn('⚠ Suspicious action detected:', reason);
                setTimeout(() => overlay.style.display = 'none', 7000);
                fetch('/report-screenshot/', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{reason, userAgent: navigator.userAgent}})
                }});
            }};

            // Detect devtools via resize (works desktop)
            let open = false;
            setInterval(() => {{
                if ((window.outerWidth - window.innerWidth > 160) || (window.outerHeight - window.innerHeight > 160)) {{
                    if (!open) {{
                        open = true;
                        showWatermark('devtools_opened');
                    }}
                }} else {{
                    open = false;
                }}
            }}, 1000);

            // Detect print
            window.addEventListener('beforeprint', () => showWatermark('print_attempt'));
            window.addEventListener('afterprint', () => overlay.style.display = 'none');

            // Detect right-click (desktop)
            document.addEventListener('contextmenu', (e) => {{
                e.preventDefault();
                showWatermark('contextmenu_attempt');
            }});

            // Detect mobile screenshot (visibility/tab switch)
            document.addEventListener('visibilitychange', () => {{
                if (document.hidden) showWatermark('mobile_screenshot_or_tab_switch');
            }});

            // Get precise browser location (user consent)
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition((pos) => {{
                    const {{ latitude, longitude }} = pos.coords;
                    fetch('/update-location/', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{latitude, longitude}})
                    }});
                    console.log('✅ Precise location:', latitude, longitude);
                }}, (err) => console.warn('Geolocation denied:', err));
            }}

            // Prevent re-flash across pages
            if (!sessionStorage.getItem('wmInitialized')) {{
                sessionStorage.setItem('wmInitialized', 'true');
            }} else {{
                overlay.style.display = 'none';
            }}
        }})();
        </script>
        """

        content = response.content.decode("utf-8")
        if "</body>" in content:
            response.content = content.replace("</body>", watermark_html + "</body>")
        else:
            response.content += watermark_html
        return response

    