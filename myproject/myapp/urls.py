from django.urls import path
from . import views
from myapp import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('certificates/', views.certificate_view, name='certificates'),
    path('projects/', views.project_view, name='projects'),
    path('skills/', views.skill_view, name='skills'),
    path('contact/', views.contact_view, name='contact'),
    path('email/', views.email_view, name='email'),
    path('profile/', views.profile_view, name='profile'),
    path('resume/', views.resume_view, name='resume'),
    path('social/', views.social_view, name='social'),
    path('contact_success/', views.contact_success, name='contact_success'),
    path('project_details/', views.project_detail_view, name='project_details'),
]