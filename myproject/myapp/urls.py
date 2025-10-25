# myproject/myapp/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Certificates
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('certificates', views.certificate_list, name='certificate_list_no_slash'),

    # Projects
    path('projects/', views.project_view, name='projects'),
    path('projects', views.project_view, name='projects_no_slash'),

    # Skills
    path('skills/', views.skills, name='skills'),
    path('skills', views.skills, name='skills_no_slash'),

    # Contact
    path('contact/', views.contact_view, name='contact'),
    path('contact', views.contact_view, name='contact_no_slash'),

    # Email
    path('email/', views.email_view, name='email'),
    path('email', views.email_view, name='email_no_slash'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile', views.profile_view, name='profile_no_slash'),

    # Resume
    path('resume/', views.resume_view, name='resume'),
    path('resume', views.resume_view, name='resume_no_slash'),

    # Social
    path('social/', views.social_page, name='page'),
    path('social', views.social_page, name='page_no_slash'),

    # Contact Success
    path('contact_success/', views.contact_success, name='contact_success'),
    path('contact_success', views.contact_success, name='contact_success_no_slash'),

    # Project Details
    path('project_details/', views.project_detail_view, name='project_details'),
    path('project_details', views.project_detail_view, name='project_details_no_slash'),
    
    path('project/<int:project_id>/', views.project_detail_view, name='project_detail'),
    path('project/<int:project_id>', views.project_detail_view, name='project_detail_no_slash'),



    # Base
    path('base/', views.base_view, name='base'),
    path('base', views.base_view, name='base_no_slash'),

    
    path("report-screenshot/", views.report_screenshot, name="report_screenshot"),
    path("report-location/", views.report_location, name="report_location"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
