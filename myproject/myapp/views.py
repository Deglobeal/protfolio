from django.shortcuts import render, get_object_or_404
from .models import Project, Certificate, Skill
from .forms import ContactForm

def home(request):
    skills = Skill.objects.all()
    projects = Project.objects.all()[:3]
    certificates = Certificate.objects.all()[:3]
    
    return render(request, 'main/home.html', {
        'skills': skills,
        'projects': projects,
        'certificates': certificates
    })

def profile(request):
    return render(request, 'main/profile.html')

def resume(request):
    return render(request, 'main/resume.html')

def certificates(request):
    certificates = Certificate.objects.all()
    return render(request, 'main/certificates.html', {'certificates': certificates})

def skills(request):
    skills = Skill.objects.all()
    return render(request, 'main/skills.html', {'skills': skills})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'main/contact_success.html')
    else:
        form = ContactForm()
    
    return render(request, 'main/contact.html', {'form': form})

def social(request):
    return render(request, 'main/social.html')

def email(request):
    return render(request, 'main/email.html')

def projects(request):
    projects = Project.objects.all()
    return render(request, 'main/projects.html', {'projects': projects})

def project_detail(request, pk):
    project = get_object_or_404(Project, id=pk)
    return render(request, 'main/project_detail.html', {'project': project})