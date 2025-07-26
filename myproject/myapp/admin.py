from django.contrib import admin
from .models import (
    Certificate, Project, Skill, ContactSubmission,
    EmailTemplate, Profile, Resume, SocialProfile
)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'issuing_organization', 'issue_date')
    search_fields = ('title', 'issuing_organization')
    list_filter = ('issue_date',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'timeline', 'role')
    search_fields = ('title', 'technologies', 'role')
    list_filter = ('timeline',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'competency_level', 'skill_level')
    list_filter = ('category',)
    search_fields = ('name', 'description')

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at')
    list_filter = ('submitted_at',)
    search_fields = ('name', 'email', 'subject')

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('template_type', 'subject')
    list_filter = ('template_type',)
    search_fields = ('subject',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'location', 'email', 'phone')
    search_fields = ('name', 'email', 'location')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = ('platform', 'handle', 'followers')
    list_filter = ('platform',)
    search_fields = ('handle', 'description')
