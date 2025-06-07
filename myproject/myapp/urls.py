from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('resume/', views.resume, name='resume'),
    path('certificate/', views.certificate, name='certificate'),
    path('skills/', views.skills, name='skills'),
    path('contact/', views.contact, name='contact'),
    path('social/', views.social, name='social'),
    path('email/', views.email, name='email'),
    path('project/', views.project, name='project'),
]