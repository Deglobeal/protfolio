from django.shortcuts import render
from .models import (
    Certificate, Project, Skill, ContactSubmission, 
    EmailTemplate, Profile, Resume, SocialProfile
)

def certificate_view(request):
    certificates = Certificate.objects.all()
    return render(request, 'main/certificate.html', {'certificates': certificates})

def project_view(request):
    featured_projects = Project.objects.filter(is_featured=True)
    additional_projects = Project.objects.filter(is_featured=False)
    return render(request, 'main/project.html', {
        'featured_projects': featured_projects,
        'additional_projects': additional_projects
    })

def skill_view(request):
    skills = Skill.objects.all().order_by('category', 'name')
    return render(request, 'main/skills.html', {'skills': skills})

def contact_view(request):
    if request.method == 'POST':
        # Process form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactSubmission.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        return render(request, 'main/contact_success.html')
        
    return render(request, 'main/contact.html')

def email_view(request):
    templates = EmailTemplate.objects.all()
    return render(request, 'main/email.html', {'templates': templates})

def profile_view(request):
    profile = Profile.objects.first()
    return render(request, 'main/profile.html', {'profile': profile})

def resume_view(request):
    resume = Resume.objects.first()
    return render(request, 'main/resume.html', {'resume': resume})

def social_view(request):
    profiles = SocialProfile.objects.all()
    return render(request, 'main/social.html', {'profiles': profiles})

def home_view(request):
    return render(request, 'main/home.html')

def contact_success_view(request): 
    return render(request, 'main/contact_success.html')

def project_detail_view(request):
    return render(request, 'main/project_detail.html')
