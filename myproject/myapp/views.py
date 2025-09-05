from django.shortcuts import render
from .models import (
    Certificate, Project, Skill, ContactSubmission, 
    EmailTemplate, Profile, Resume, SocialProfile, SiteProfile, Service,
    Education, BackgroundInterest, 
    ProfessionalPhilosophy, ProfessionalExperience,
    SkillSummary, SkillCategory, LearningPath, SocialPlatform
)

# veiw for certificate

def certificate_list(request):
    certificates = Certificate.objects.all().order_by('-issue_date')
    learning_paths = LearningPath.objects.all().order_by('-completion_date')
    
    # Get category choices from model
    certificate_categories = Certificate.CATEGORY_CHOICES
    
    # Handle filtering if category parameter is provided
    category = request.GET.get('category')
    if category:
        certificates = certificates.filter(category=category)
    
    # Handle search if query parameter is provided
    search_query = request.GET.get('q')
    if search_query:
        certificates = certificates.filter(title__icontains=search_query) | \
                      certificates.filter(issuer__icontains=search_query) | \
                      certificates.filter(description__icontains=search_query)
    
    context = {
        'certificates': certificates,
        'learning_paths': learning_paths,
        'selected_category': category,
        'search_query': search_query or '',
        'certificate_categories': certificate_categories,
    }
    
    return render(request, 'main/certificate.html', context)

# view for project
def project_view(request):
    featured_projects = Project.objects.filter(is_featured=True)
    additional_projects = Project.objects.filter(is_featured=False)
    return render(request, 'main/project.html', {
        'featured_projects': featured_projects,
        'additional_projects': additional_projects
    })


# view for skill
def skills(request):
    # Get only skills that have content
    skills = Skill.objects.exclude(description__isnull=True).exclude(description__exact="")
    
    categories = [{'code': code, 'label': label} for code, label in SkillCategory.choices]
    summary = SkillSummary.load()
    
    context = {
        'skills': skills,
        'categories': categories,
        'summary': summary,
    }
    return render(request, 'main/skills.html', context)


# view for contact
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


# view for email templates
def email_view(request):
    templates = EmailTemplate.objects.all()
    return render(request, 'main/email.html', {'templates': templates})

# views.py - Update profile_view
def profile_view(request):
    profile = Profile.objects.first()
    profile_details = []  # Removed access to unknown 'details' attribute
    educations = Education.objects.filter(profile=profile) if profile else []
    experiences = ProfessionalExperience.objects.filter(profile=profile) if profile else []
    background_interests = BackgroundInterest.objects.filter(profile=profile) if profile else []
    philosophies = ProfessionalPhilosophy.objects.filter(profile=profile) if profile else []
    
    return render(request, 'main/profile.html', {
        'profile': profile,
        'profile_details': profile_details,
        'educations': educations,
        'experiences': experiences,
        'background_interests': background_interests,
        'philosophies': philosophies
    })


# view for resume
def resume_view(request):
    resume = Resume.objects.first()
    experiences = ProfessionalExperience.objects.all().order_by('-start_date')
    educations = Education.objects.all().order_by('-start_date')
    
    # Get skills by category
    frontend_skills = Skill.objects.filter(category='FRONTEND')
    backend_skills = Skill.objects.filter(category='BACKEND')
    
    certificates = Certificate.objects.all().order_by('-issue_date')
    
    # Languages data (you might need to create a Language model)
    languages = [
        {'name': 'English', 'proficiency': 'Native Proficiency', 'percentage': 100},
        {'name': 'Igbo', 'proficiency': 'Professional Proficiency', 'percentage': 100},
    ]
    
    # Interests data (using BackgroundInterest model)
    interests = BackgroundInterest.objects.filter(category='personal')
    
    context = {
        'resume': resume,
        'experiences': experiences,
        'educations': educations,
        'frontend_skills': frontend_skills,
        'backend_skills': backend_skills,
        'certificates': certificates,
        'languages': languages,
        'interests': interests,
    }
    
    return render(request, 'main/resume.html', context)

# view for social profiles
def social_view(request):
    profiles = SocialProfile.objects.all()
    return render(request, 'main/social.html', {'profiles': profiles})

# new view for social platforms
def social_page(request):
    categories = [
        {"slug": "professional", "title": "Professional Networks"},
        {"slug": "social",       "title": "Social Media Platforms"},
        {"slug": "additional",   "title": "Additional Platforms"},
    ]
    context = {
        "categories": categories,
    }
    for cat in categories:
        platforms = SocialPlatform.objects.filter(category=cat["slug"])
        context[cat["slug"]] = [
            {
                "name": platform.name,
                "url": platform.url,
                "category": platform.category,
            }
            for platform in platforms
        ]
    return render(request, "main/social.html", context)


# view for home page
def home(request):
    profile = SiteProfile.objects.first()
    services = Service.objects.all()
    return render(request, 'main/home.html', {
        'profile': profile,
        'services': services,
    })


# view for contact success
def contact_success(request):
    return render(request, 'main/contact_success.html')


# view for project detail
def project_detail_view(request):
    return render(request, 'main/project_detail.html')

# base view
def base_view(request):
    return render(request, 'base.html')