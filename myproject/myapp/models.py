from django.db import models
from django.core.validators import URLValidator

# model.py certification model
# model for storing certification details

class Certificate(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Development'),
        ('cloud', 'Cloud & DevOps'),
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('security', 'Security'),
    ]
    
    issuer = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    issue_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='certificates/', null=True, blank=True)
    verification_url = models.URLField(blank=True)
    certificate_url = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.issuer} - {self.title}"
    
    @property
    def display_date(self):
        return self.issue_date.strftime("%B %Y")
    
    @property
    def display_valid_until(self):
        if self.valid_until:
            return self.valid_until.strftime("%B %Y")
        return "No expiration"

class LearningPath(models.Model):
    title = models.CharField(max_length=200)
    completion_date = models.DateField()
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default="fas fa-laptop-code")
    
    def __str__(self):
        return self.title
    
    @property
    def display_date(self):
        return self.completion_date.strftime("%Y")

#  models.py - Project model
# model for detailing projects in portfolio

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    key_features = models.TextField()
    technologies = models.TextField()
    live_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    timeline = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='projects/', null=True, blank=True)

    def __str__(self):
        return self.title

# models.py - Skill model
# model for categorizing and detailing skills


class SkillCategory(models.TextChoices):
    LANGUAGE = "LANGUAGE", "Programming Languages"
    FRONTEND = "FRONTEND", "Frontend Frameworks"
    BACKEND  = "BACKEND",  "Backend Technologies"
    DATABASE = "DATABASE", "Database Technologies"
    DEVOPS   = "DEVOPS",   "Development Tools"
    TESTING  = "TESTING",  "Testing & QA"
    DESIGN   = "DESIGN",   "Design & UI Tools"
    SOFT     = "SOFT",     "Professional Skills"
    SUMMARY  = "SUMMARY",  "Skills Summary"

class Skill(models.Model):
    """
    A single skill (card) – used across all categories.
    """
    title = models.CharField(max_length=50, default="Programming Languages")
    category = models.CharField(max_length=20, choices=SkillCategory.choices)
    icon_class = models.CharField(
        max_length=50,
        default="fab fa-code",
        help_text="FontAwesome class, e.g. 'fab fa-js'"
    )
    description = models.TextField()
    level = models.CharField(
        max_length=20, 
        default="Beginner",
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
            ("Expert", "Expert"),
        ]
    )
    rating = models.PositiveSmallIntegerField(default=5)
    tags = models.TextField(
        blank=True,
        help_text="Comma-separated list of tags"
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["category", "order"]

    def __str__(self):
        return f"{self.title} ({self.category})"

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]
    
    def get_experience_years(self):
        """Return experience years based on skill level"""
        level_to_years = {
            "Beginner": "1",
            "Intermediate": "1-2",
            "Advanced": "2-3",
            "Expert": "3+"
        }
        return level_to_years.get(self.level, "2+")
    

# models.py - SkillSummary model
class SkillSummary(models.Model):
    """
    One-row model for the “Skills Summary” paragraph & CTA.
    """
    summary = models.TextField(
        default="My technical expertise spans the full web development stack…"
    )

    class Meta:
        verbose_name_plural = "Skill Summary"

    def __str__(self):
        return "Skills Summary (Singleton)"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
    


# models.py - ContactSubmission model
# model for storing contact form submissions

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

# models.py - EmailTemplate model
# model for email templates used in contact form

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

    def __str__(self):
        return self.subject

# models.py -  Profile model
#model for profile section in profile.html template

class Profile(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile/', null=True, blank=True)
    about_me = models.TextField()
    experience_years = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

    @property
    def experience_years_display(self):
        return f"{self.experience_years}+ Years" if self.experience_years else "5+ Years"
        
class ProfileDetail(models.Model):
    DETAIL_TYPES = [
        ('location', 'Location'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('experience', 'Experience'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='details')
    detail_type = models.CharField(max_length=20, choices=DETAIL_TYPES)
    value = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=50, default='fas fa-circle')
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order']


class ContactDetail(models.Model):
    CONTACT_TYPES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('location', 'Location'),
        ('website', 'Website'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='contact_details')
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPES)
    value = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.contact_type}: {self.value}"

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['-end_date', 'order']
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"

class ProfessionalExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    technologies = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['-end_date', 'order']
    
    def __str__(self):
        return f"{self.position} at {self.company}"

class BackgroundInterest(models.Model):
    CATEGORY_CHOICES = [
        ('professional', 'Professional Background'),
        ('personal', 'Personal Interests'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='background_interests')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order']
    
    def __str__(self):
        return f"{self.category}: {self.title}"

class ProfessionalPhilosophy(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='philosophies')
    quote = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = "Professional philosophies"
    
    def __str__(self):
        return f"Philosophy: {self.quote[:50]}..."


# models.py - Resume model
# model for resume details



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

    def __str__(self):
        return self.title

# models.py - SocialProfile model
# model for social media profiles

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

    def __str__(self):
        return f"{self.platform} - {self.handle}"

# models.py - SiteProfile model
# model for site-wide profile settings

class SiteProfile(models.Model):
    """
    Singleton model that stores the global site-level copy
    (hero text, about bullets, meta description, etc.)
    """
    hero_heading = models.CharField(max_length=100, default="Hi, I'm Gerard Ugwu")
    hero_subtitle = models.TextField(
        default="Backend Developer • Python Enthusiast • ALX ProDev Learner • Web Developer\n"
                "Crafting modern, scalable, and responsive web applications…"
    )
    hero_cta_primary_text = models.CharField(max_length=30, default="View My Work")
    hero_cta_primary_link = models.CharField(max_length=255, default="/projects", validators=[URLValidator()])
    hero_cta_secondary_text = models.CharField(max_length=30, default="Get In Touch")
    hero_cta_secondary_link = models.CharField(max_length=255, default="/contact", validators=[URLValidator()])

    about_paragraphs = models.JSONField(
        default=list,
        help_text="Enter each paragraph as a list item in the admin."
    )

    featured_projects_blurb = models.TextField(
        default="My portfolio showcases e-commerce platforms, SaaS dashboards & automation tools…"
    )
    featured_projects_cta_text = models.CharField(max_length=30, default="Explore All Projects")
    featured_projects_cta_link = models.CharField(max_length=255, default="/projects", validators=[URLValidator()])

    def __str__(self):
        return "Home-Page Singleton"

    class Meta:
        verbose_name = "Site Profile"

# models.py - Service model
# model for services offered section

class Service(models.Model):
    """
    The three cards under "What I Do".
    """
    title = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=50, help_text="FontAwesome class, e.g. fas fa-code")
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title

# models.py - SocialPlatform model
# model for social media platforms details

class SocialPlatform(models.Model):
    CATEGORY_CHOICES = (
        ('professional', 'Professional Networks'),
        ('social',       'Social Media'),
        ('additional',   'Additional Platforms'),
    )

    name        = models.CharField(max_length=50)
    icon_class  = models.CharField(max_length=40)   # e.g. "fab fa-linkedin"
    url         = models.URLField()
    category    = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    followers   = models.CharField(max_length=20, blank=True)
    posts       = models.CharField(max_length=20, blank=True)
    description = models.TextField()
    highlights  = models.TextField(help_text="Bullet list, one line per bullet")
    popular     = models.TextField(help_text="Popular items, one line per item")

    def __str__(self):
        return self.name