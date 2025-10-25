# myproject/myapp/views.py
# Import necessary modules and models
# views.py

# import statements
# helps to render templates and interact with models
# improves view functions for better functionality
from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    Certificate, Project, Skill, 
    EmailTemplate, Profile, Resume, SocialProfile, SiteProfile, Service,
    Education, BackgroundInterest, 
    ProfessionalPhilosophy, ProfessionalExperience,
    SkillSummary, SkillCategory, LearningPath, SocialPlatform, EmailAddress, EmailTemplates, AlternativeMethod,
    EmailGuidelineSection, SecurityItem, FAQ
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .models import ContactMessage, WatermarkRecord, AutoReplyTemplate
from django.contrib import messages
from django.utils.timezone import now
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string



logger = logging.getLogger(__name__)

# view for certificate
# Updated to include filtering and search functionality
# Also retrieves category choices from the model
# Updated template context to include categories and search query
# Updated to order certificates and learning paths by date

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
# Updated to separate featured and additional projects
# Updated template context to include both lists
# Updated to order projects by date added
# Updated to filter projects based on a 'featured' boolean field
# Updated template to display featured and additional projects separately

def project_view(request):
    featured_projects = Project.objects.filter(is_featured=True)
    additional_projects = Project.objects.filter(is_featured=False)
    
    return render(request, 'main/project.html', {
        'featured_projects': featured_projects,
        'additional_projects': additional_projects
    })


# view for skill
# Updated to filter out skills without content
# Updated to include skill categories in context
# Updated to load skill summary from SkillSummary model
# Updated template to display skills by category and show summary

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
# Updated to handle form submission and save to ContactSubmission model
# Updated to render a success page after submission
# Updated template to include a contact form
# Updated to validate form inputs (basic validation)
# Updated to use POST method for form submission
# Updated to prevent duplicate submissions on page refresh

def contact_view(request):
    if request.method == 'POST':
        # Process form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        try:
            # Save the message to the database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )

            # Send auto-reply email
            try:
                send_auto_reply_email(name, email, subject, message_text)
            except Exception as email_error:
                # Log email error but don't crash the form submission
                logger.error(f"Auto-reply email failed: {email_error}")

            messages.success(request, '✅ Your message has been received! You should receive a confirmation email shortly.')
            return redirect('contact_success')

        except Exception as e:
            messages.error(request, '⚠️ There was an error saving your message. Please try again.')
            logger.error(f"Contact form error: {e}")

    return render(request, 'main/contact.html')

def send_auto_reply_email(name, email, original_subject, original_message):
    """Send auto-reply email to the person who submitted the contact form"""
    
    # Get the active template
    template = AutoReplyTemplate.get_active_template()
    
    if not template:
        # Use default template if none exists
        template_subject = "Thank you for contacting Gerard Ugwu"
        template_message = f"""Hello {name},

Thank you for reaching out! I've received your message and will get back to you within 24 hours.

Here's a copy of your message:
Subject: {original_subject}
Message: {original_message}

Best regards,
Gerard Ugwu
Backend Developer"""
    else:
        template_subject = template.subject
        template_message = template.message.format(
            name=name,
            subject=original_subject,
            message=original_message
        )

    # Send email
    send_mail(
        subject=template_subject,
        message=strip_tags(template_message),  # Plain text version
        from_email='kachimaxy1@gmail.com',
        recipient_list=[email],
        html_message=template_message,  # HTML version
        fail_silently=False,
    )
    
    logger.info(f"Auto-reply email sent to {email}")



# view for email templates
# Updated to list all email templates from the database
# Updated template to display email templates in a user-friendly format
# Updated to order email templates by name

def email_view(request):
    templates = EmailTemplate.objects.all()
    return render(request, 'main/email.html', {'templates': templates})

# views.py - Update profile_view
# Updated to remove access to unknown 'details' attribute
# Updated to handle case where no profile exists

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
# Updated to include skills by category
# Updated to include languages and interests data
# Updated template to display skills, languages, and interests
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
# Updated to list all social profiles from the database
# Updated template to display social profiles in a user-friendly format
# Updated to order social profiles by name

def social_view(request):
    profiles = SocialProfile.objects.all()
    return render(request, 'main/social.html', {'profiles': profiles})

# new view for social platforms
# Updated to categorize social platforms
# Updated template to display platforms by category
# Updated to order platforms by name

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
# Updated to include site profile and services
# Updated template to display site profile and services
# Updated to order services by name

def home(request):
    profile = SiteProfile.objects.first()
    services = Service.objects.all()
    
    return render(request, 'main/home.html', {
        'profile': profile,
        'services': services,
    })


# view for contact success
# Renders a simple success page after contact form submission
# Updated template to thank user for submission
# Updated to provide a link back to the contact form or home page

def contact_success(request):
    return render(request, 'main/contact_success.html')


# view for project detail
# Renders a detailed view of a single project
# Updated to fetch project by ID or slug (not implemented here) 
# Updated template to display detailed project information


def project_detail_view(request, project_id=None):
    """
    View for individual project details.
    If project_id is provided, show that specific project.
    Otherwise, show a default project detail page or list.
    """
    # If a specific project ID is provided
    if project_id:
        try:
            project = get_object_or_404(Project, id=project_id)
            
            # Get related projects (excluding current project)
            related_projects = Project.objects.exclude(id=project_id)[:3]
            
            context = {
                'project': project,
                'related_projects': related_projects,
                'projects': Project.objects.all()  # For navigation
            }
            return render(request, 'main/project_detail.html', context)
        except Project.DoesNotExist:
            # If project doesn't exist, show 404 or redirect
            from django.http import Http404
            raise Http404("Project not found")
    
    # If no specific project, show the first project or a list
    projects = Project.objects.all()
    if projects.exists():
        # FIXED: Use the correct URL name 'project_detail' (not 'project_details')
        first_project = projects.first()
        if first_project:
            return redirect('project_detail', project_id=first_project.id)
    
    # No projects exist
    context = {
        'projects': projects
    }
    return render(request, 'main/project_detail.html', context)

# base view
# Renders the base template for the site
# Updated template to include common site elements (header, footer, etc.)
# Updated to be used as a base for other templates
def base_view(request):
    return render(request, 'base.html')


# view for email_page
# Renders a page for email-related content
# Updated template to display email-related information


# views.py - Email view
def email(request):
    context = {
        # Email addresses
        'emails': EmailAddress.objects.filter(is_active=True),
        
        # Email templates - Fixed: using EmailTemplate instead of EmailTemplates
        'templates': EmailTemplates.objects.filter(is_active=True),
        
        # Email guidelines
        'guideline_sections': EmailGuidelineSection.objects.filter(is_active=True).prefetch_related(
            'items', 'subsections', 'subsections__items'
        ),
        
        # Security items
        'security_items': SecurityItem.objects.filter(is_active=True).prefetch_related('points'),
        
        # Alternative methods
        'methods': AlternativeMethod.objects.filter(is_active=True),
        
        # FAQs
        'faqs': FAQ.objects.filter(is_active=True),
        
        # CTA settings
        'default_contact_email': 'kachimaxy1@gmail.com',
        'contact_form_redirect_to_gmail': True,
        'contact_form_subject': 'Contact Form Inquiry',
        'contact_form_url': '/contact',
    }
    
    return render(request, 'email.html', context)


# Helper function
def get_client_ip(request):
    """Extract IP address (supports proxy headers)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@csrf_exempt
def report_screenshot(request):
    """
    Called when a screenshot, print, devtools, or contextmenu event is detected.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            path = data.get("path", request.path)
            event_type = data.get("event_type", "screenshot")
            ip = get_client_ip(request)
            user = request.user if request.user.is_authenticated else None

            record = WatermarkRecord.objects.create(
                path=path,
                ip_address=ip,
                user=user,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                event_type=event_type,
            )

            logger.warning(f"⚠ {event_type.upper()} on {path} from {ip} (user={user})")

            return JsonResponse({"status": "ok", "message": "Event logged", "id": record.id}) # type: ignore

        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON in report_screenshot")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"❌ report_screenshot failed: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)


@csrf_exempt
def report_location(request):
    """
    Receives GPS data from browser (if user allowed geolocation access)
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            ip = get_client_ip(request)
            user = request.user if request.user.is_authenticated else None
            path = data.get("path", "unknown")

            latitude = data.get("latitude")
            longitude = data.get("longitude")
            accuracy = data.get("accuracy")

            record = WatermarkRecord.objects.create(
                path=path,
                ip_address=ip,
                user=user,
                event_type="location_update",
                latitude=latitude,
                longitude=longitude,
                accuracy=accuracy,
            )

            logger.info(f"📍 Location update from {ip} — ({latitude}, {longitude}) ±{accuracy}m")

            return JsonResponse({"status": "ok", "message": "Location logged", "id": record.id}) # type: ignore

        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON in report_location")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"❌ report_location failed: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)
