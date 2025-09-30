# myproject/myapp/urls.py
# Import necessary modules and views
# links URL patterns to corresponding view functions
# helps to organize URL routing for the app

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from myapp import views

# Define URL patterns
# Each path maps a URL to a view function
# Updated to include new views and remove deprecated ones
# Updated names for better clarity and consistency
urlpatterns = [
    path('', views.home, name='home'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('projects/', views.project_view, name='projects'),
    path('skills/', views.skills, name='skills'),
    path('contact/', views.contact_view, name='contact'),
    path('email/', views.email_view, name='email'),
    path('profile/', views.profile_view, name='profile'),
    path('resume/', views.resume_view, name='resume'),
    path('social/', views.social_page, name='page'),
    path('contact_success/', views.contact_success, name='contact_success'),
    path('project_details/', views.project_detail_view, name='project_details'),
    path('base/', views.base_view, name='base'),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)