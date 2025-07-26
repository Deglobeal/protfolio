from django.db import models

class Certificate(models.Model):
    title = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100)
    verification_url = models.URLField()
    description = models.TextField()
    skills_validated = models.TextField()

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    key_features = models.TextField()
    technologies = models.TextField()
    live_url = models.URLField()
    github_url = models.URLField()
    timeline = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    is_featured = models.BooleanField(default=False) 

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('lang', 'Programming Languages'),
        ('frontend', 'Frontend Frameworks'),
        ('backend', 'Backend Technologies'),
        ('db', 'Database Technologies'),
        ('tools', 'Development Tools'),
        ('testing', 'Testing & QA'),
        ('design', 'Design & UI Tools'),
        ('soft', 'Professional Skills'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    competency_level = models.CharField(max_length=100)
    description = models.TextField()
    skill_level = models.PositiveIntegerField()  # 1-5 scale

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

class EmailTemplate(models.Model):
    TEMPLATE_CHOICES = [
        ('project', 'Project Inquiry'),
        ('collab', 'Collaboration Request'),
        ('tech', 'Technical Question'),
        ('networking', 'Professional Networking'),
    ]
    
    template_type = models.CharField(max_length=20, choices=TEMPLATE_CHOICES)
    subject = models.CharField(max_length=255)
    content = models.TextField()

class Profile(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    about_me = models.TextField()
    education = models.TextField()
    experience = models.TextField()
    background = models.TextField()
    interests = models.TextField()
    philosophy = models.TextField()

class Resume(models.Model):
    title = models.CharField(max_length=100)
    summary = models.TextField()
    competencies = models.TextField()
    experience = models.TextField()
    education = models.TextField()
    certifications = models.TextField()
    projects = models.TextField()
    awards = models.TextField()
    languages = models.TextField()
    volunteer = models.TextField()

class SocialProfile(models.Model):
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('stackoverflow', 'Stack Overflow'),
        ('devto', 'Dev.to'),
        ('dribbble', 'Dribbble'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    handle = models.CharField(max_length=100)
    description = models.TextField()
    followers = models.PositiveIntegerField()
    content_types = models.TextField()