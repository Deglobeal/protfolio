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


class WatermarkMiddleware(MiddlewareMixin):
    """
    Injects watermark into sensitive HTML pages.
    Watermark stays hidden during normal browsing,
    only appears if user attempts a screenshot or printing.
    """

    SENSITIVE_PATHS = [
        r'^/$', r'^/certificates', r'^/projects', r'^/skills',
        r'^/contact', r'^/email', r'^/profile', r'^/resume',
        r'^/social', r'^/contact_success', r'^/project_details',
        r'^/project/\d+', r'^/base',
    ]

    IPINFO_TOKEN = "fd78618ee198d9"  # ✅ your ipinfo.io token

    def process_response(self, request, response):
        try:
            content_type = response.get('Content-Type', '')
            if "text/html" in content_type and response.status_code == 200:
                for pattern in self.SENSITIVE_PATHS:
                    if re.match(pattern, request.path):
                        response = self._inject_html_watermark(request, response)
                        break
        except Exception as e:
            logger.exception("WatermarkMiddleware error: %s", e)

        return response

    # -------------------- IP + Location Logic --------------------

    def get_client_ip(self, request):
        """Get the user's real IP even behind proxies."""
        ip_headers = [
            'HTTP_CF_CONNECTING_IP',      # Cloudflare
            'HTTP_X_REAL_IP',             # Nginx/Proxy
            'HTTP_X_FORWARDED_FOR',       # Standard proxies
            'REMOTE_ADDR',                # Default
        ]
        for header in ip_headers:
            ip = request.META.get(header)
            if ip:
                # X-Forwarded-For may contain multiple IPs
                ip = ip.split(',')[0].strip()
                if self._is_valid_ip(ip):
                    return ip
        return '127.0.0.1'

    def _is_valid_ip(self, ip):
        """Simple validation for IPv4/IPv6"""
        return bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip) or ':' in ip)

    def get_location_data(self, ip_address):
        """Retrieve location data for IP using ipinfo.io"""
        # Handle localhost or private IPs
        if ip_address in ['127.0.0.1', '::1', 'localhost'] or ip_address.startswith(
            ('10.', '192.168.', '172.16.', '172.17.', '172.18.',
             '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
             '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
             '172.29.', '172.30.', '172.31.')
        ):
            return {
                'city': 'Local Network',
                'region': 'Development',
                'country': 'Local',
                'location_string': 'Local Network/Development',
                'google_maps_url': 'https://www.google.com/maps'
            }

        try:
            url = f"https://ipinfo.io/{ip_address}?token={self.IPINFO_TOKEN}"
            logger.info(f"Looking up IP location: {ip_address}")
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                logger.warning(f"Failed IP lookup ({response.status_code}): {ip_address}")
                return {'location_string': 'Unknown Location', 'google_maps_url': '#'}

            data = response.json()
            logger.debug(f"IP data: {data}")

            city = data.get('city', 'Unknown City')
            region = data.get('region', 'Unknown Region')
            country = data.get('country', 'Unknown Country')
            org = data.get('org', 'Unknown ISP')
            loc = data.get('loc', '')  # "lat,lon"

            google_maps_url = "https://www.google.com/maps"
            if loc and ',' in loc:
                lat, lon = loc.split(',')
                google_maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=10"

            location_string = f"{city}, {region}, {country}".replace('Unknown, ', '').strip(', ')

            return {
                'city': city,
                'region': region,
                'country': country,
                'isp': org,
                'coordinates': loc,
                'location_string': location_string,
                'google_maps_url': google_maps_url,
            }

        except requests.exceptions.Timeout:
            logger.warning(f"Location lookup timed out for {ip_address}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Location lookup error for {ip_address}: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in location lookup: {e}")

        # Default fallback
        return {
            'city': 'Unknown',
            'region': 'Unknown',
            'country': 'Unknown',
            'location_string': 'Location Unknown',
            'google_maps_url': 'https://www.google.com/maps'
        }

    # -------------------- Watermark Injection --------------------

    def _inject_html_watermark(self, request, response):
        """Inject watermark overlay with user, IP, and location info"""
        client_ip = self.get_client_ip(request)
        location_data = self.get_location_data(client_ip)
        location_info = location_data.get('location_string', 'Location Unknown')
        google_maps_url = location_data.get('google_maps_url', '#')
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')

        user_info = (
            f"USER: {request.user.username} | {request.user.email}"
            if getattr(request, "user", None) and request.user.is_authenticated
            else "USER: Anonymous Visitor"
        )

        ip_warning = f"⚠️ UNAUTHORIZED SCREENSHOT - IP: {client_ip} - {location_info} - {current_time} ⚠️"
        legal_warning = (
            "LEGAL NOTICE: This content is protected by copyright. "
            "Unauthorized screenshot, distribution, or reproduction is strictly prohibited."
        )
        user_identifier = f"{user_info} | IP: {client_ip} | LOC: {location_info} | TIME: {current_time}"

        # Escape everything
        watermark_html = f"""
<!-- Watermark Protection System -->
<div id="__watermark_overlay" style="
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 999999999;
  -webkit-user-select: none;
  -moz-user-select: none;
  user-select: none;
  overflow: hidden;
">
  <!-- Main warning banner - Top -->
  <div style="
    position: absolute;
    top: 15%;
    left: 5%;
    right: 5%;
    text-align: center;
    font-size: clamp(20px, 3vw, 36px);
    color: rgba(255, 0, 0, 0.8);
    font-weight: 900;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    white-space: nowrap;
    mix-blend-mode: multiply;
    padding: 15px;
    background: rgba(255,255,255,0.1);
    border: 2px solid rgba(255,0,0,0.3);
    border-radius: 8px;
  ">
    {escape(ip_warning)}
  </div>
  
  <!-- Legal warning - Middle -->
  <div style="
    position: absolute;
    top: 45%;
    left: 5%;
    right: 5%;
    text-align: center;
    font-size: clamp(14px, 1.8vw, 20px);
    color: rgba(200, 0, 0, 0.7);
    font-weight: 700;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    line-height: 1.4;
    mix-blend-mode: multiply;
    padding: 12px;
    background: rgba(255,255,255,0.05);
    border-left: 3px solid rgba(255,0,0,0.4);
    border-right: 3px solid rgba(255,0,0,0.4);
  ">
    {escape(legal_warning)}
  </div>
  
  <!-- Diagonal watermark with user info -->
  <div style="
    position: absolute;
    top: 30%;
    left: 5%;
    right: 5%;
    text-align: center;
    font-size: clamp(16px, 2.5vw, 28px);
    color: rgba(0, 0, 255, 0.4);
    transform: rotate(-30deg);
    font-weight: 800;
    text-shadow: 2px 2px 3px rgba(0, 0, 0, 0.2);
    white-space: nowrap;
    mix-blend-mode: multiply;
  ">
    {escape(user_identifier)}
  </div>
</div>

<!-- Always visible corner watermarks -->
<div id="__watermark_bottom" style="
  position: fixed;
  bottom: 10px;
  right: 10px;
  font-size: 12px;
  color: rgba(128, 0, 128, 0.7);
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
  mix-blend-mode: multiply;
  padding: 6px;
  background: rgba(255,255,255,0.8);
  border-radius: 4px;
  pointer-events: none;
  z-index: 999999998;
  -webkit-user-select: none;
  -moz-user-select: none;
  user-select: none;
  border: 1px solid rgba(128, 0, 128, 0.3);
">
  <a href="{escape(google_maps_url)}" target="_blank" style="color: inherit; text-decoration: none; cursor: pointer; pointer-events: auto;">
    PROTECTED CONTENT | LOC: {escape(location_info)} | TIME: {escape(current_time)}
  </a>
</div>

<div id="__watermark_left" style="
  position: fixed;
  bottom: 10px;
  left: 10px;
  font-size: 12px;
  color: rgba(255, 165, 0, 0.7);
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
  mix-blend-mode: multiply;
  padding: 6px;
  background: rgba(255,255,255,0.8);
  border-radius: 4px;
  pointer-events: none;
  z-index: 999999998;
  -webkit-user-select: none;
  -moz-user-select: none;
  user-select: none;
  border: 1px solid rgba(255, 165, 0, 0.3);
">
  <a target="_blank" style="color: inherit; text-decoration: none; cursor: pointer; pointer-events: auto;">
    SCREENSHOT PROTECTION | IP: {escape(client_ip)} |
  </a>
</div>

<style>
  /* Always show watermark during print */
  @media print {{
    #__watermark_overlay {{
      display: block !important;
    }}
    #__watermark_bottom, #__watermark_left {{
      display: block !important;
      background: rgba(255,255,255,0.9) !important;
    }}
  }}
  
  /* Make links in watermarks clickable */
  #__watermark_bottom a, #__watermark_left a {{
    pointer-events: auto !important;
  }}
</style>

<script>
  // Enhanced location tracking with multiple methods
  let userLocation = '{escape(location_info)}';
  let hasEnhancedLocation = false;
  let googleMapsUrl = '{escape(google_maps_url)}';
  
  // Try to get more precise location from browser if available
  function getEnhancedLocation() {{
    if (navigator.geolocation && !hasEnhancedLocation) {{
      navigator.geolocation.getCurrentPosition(
        function(position) {{
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          const accuracy = position.coords.accuracy;
          const enhancedLocation = `GPS: ${{lat.toFixed(4)}}, ${{lon.toFixed(4)}} (±${{Math.round(accuracy)}}m)`;
          const newGoogleMapsUrl = `https://www.google.com/maps?q=${{lat}},${{lon}}&z=15`;
          
          // Update watermarks with enhanced location
          const bottomWatermark = document.getElementById('__watermark_bottom');
          const leftWatermark = document.getElementById('__watermark_left');
          
          if (bottomWatermark) {{
            bottomWatermark.innerHTML = `<a href="${{newGoogleMapsUrl}}" target="_blank" style="color: inherit; text-decoration: none; cursor: pointer; pointer-events: auto;">
              PROTECTED CONTENT | LOC: ${{enhancedLocation}} | TIME: {escape(current_time)}
            </a>`;
          }}
          if (leftWatermark) {{
            leftWatermark.innerHTML = `<a href="${{newGoogleMapsUrl}}" target="_blank" style="color: inherit; text-decoration: none; cursor: pointer; pointer-events: auto;">
              SCREENSHOT PROTECTION | IP: {escape(client_ip)} |
            </a>`;
          }}
          
          userLocation = enhancedLocation;
          googleMapsUrl = newGoogleMapsUrl;
          hasEnhancedLocation = true;
          
          // Report enhanced location to backend
          reportEnhancedLocation(lat, lon, accuracy, 'browser_geolocation');
        }},
        function(error) {{
          console.log('Browser geolocation not available or denied:', error.message);
        }},
        {{
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutes
        }}
      );
    }}
  }}

  // Report enhanced GPS location to backend
  function reportEnhancedLocation(lat, lon, accuracy, source) {{
    fetch('/report-location/', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }},
      body: JSON.stringify({{
        latitude: lat,
        longitude: lon,
        accuracy: accuracy,
        source: source,
        path: window.location.pathname,
        ip: '{escape(client_ip)}',
        timestamp: new Date().toISOString(),
        google_maps_url: `https://www.google.com/maps?q=${{lat}},${{lon}}`
      }})
    }}).catch(function(err) {{ 
      console.log('Location reporting failed:', err); 
    }});
  }}

  // Show watermark during print events
  window.addEventListener('beforeprint', function() {{
    document.getElementById('__watermark_overlay').style.display = 'block';
    sendScreenshotEvent('print');
  }});
  
  window.addEventListener('afterprint', function() {{
    document.getElementById('__watermark_overlay').style.display = 'none';
  }});

  // Detect PrintScreen key and show watermark
  document.addEventListener('keyup', function(e) {{
    if (e.key === 'PrintScreen' || (e.ctrlKey && e.key === 'p') || (e.metaKey && e.key === 'p')) {{
      const wm = document.getElementById('__watermark_overlay');
      wm.style.display = 'block';
      sendScreenshotEvent('screenshot');
      setTimeout(function() {{ wm.style.display = 'none'; }}, 10000);
    }}
  }});

  // Detect right-click
  document.addEventListener('contextmenu', function(e) {{
    const wm = document.getElementById('__watermark_overlay');
    wm.style.display = 'block';
    setTimeout(function() {{ wm.style.display = 'none'; }}, 10000);
    sendScreenshotEvent('context_menu');
  }});

  // Detect dev tools opening
  let devToolsOpen = false;
  setInterval(function() {{
    const widthThreshold = window.outerWidth - window.innerWidth > 100;
    const heightThreshold = window.outerHeight - window.innerHeight > 100;
    
    if ((widthThreshold || heightThreshold) && !devToolsOpen) {{
      devToolsOpen = true;
      const wm = document.getElementById('__watermark_overlay');
      wm.style.display = 'block';
      sendScreenshotEvent('dev_tools');
      setTimeout(function() {{ wm.style.display = 'none'; }}, 10000);
    }}
  }}, 1000);

  // Report event to backend
  function sendScreenshotEvent(eventType) {{
    fetch('/report-screenshot/', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }},
      body: JSON.stringify({{
        path: window.location.pathname,
        event_type: eventType,
        ip: '{escape(client_ip)}',
        location: userLocation,
        google_maps_url: googleMapsUrl,
        timestamp: new Date().toISOString()
      }})
    }}).catch(function(err) {{ 
      console.log('Screenshot reporting failed:', err); 
    }});
  }}

  function getCSRFToken() {{
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {{
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {{
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {{
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }}
      }}
    }}
    return cookieValue;
  }}
  
  // Try to get enhanced location when page loads
  document.addEventListener('DOMContentLoaded', function() {{
    setTimeout(getEnhancedLocation, 1000);
  }});
  
  // Log watermark status
  console.log('🔒 Watermark protection active. IP: {escape(client_ip)}, Location: {escape(location_info)}');
  console.log('🗺️  Google Maps link:', '{escape(google_maps_url)}');
</script>
"""

        # Inject the watermark before </body>
        lowered = response.content.lower()
        idx = lowered.rfind(b"</body>")
        if idx != -1:
            response.content = (
                response.content[:idx]
                + watermark_html.encode("utf-8")
                + response.content[idx:]
            )
        else:
            response.content += watermark_html.encode("utf-8")

        if response.has_header("Content-Length"):
            response["Content-Length"] = str(len(response.content))

        logger.info(
            f"Watermark injected for {request.path} "
            f"[IP={client_ip}, Location={location_info}, User={getattr(request.user, 'username', 'Anonymous')}]"
        )

        return response

    