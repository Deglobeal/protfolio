from django.contrib import admin
from .models import (
    SiteProfile, Service, Certificate, Project, Skill, 
    ContactSubmission, EmailTemplate, Profile, Resume, SocialProfile,
    ContactDetail, Education, ProfessionalExperience, BackgroundInterest, ProfessionalPhilosophy,
    ProfileDetail, SkillSummary, LearningPath, SocialPlatform, EmailAddress, EmailTemplates,
    GuidelineSection, GuidelineItem,
    SecurityItem, Method, FAQ
)
# MODEL ADMINISTRATIONS FOR THE ADMIN INTERFACE
# Register models FOR PROFILE MANAGEMENT here.

@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    # Make it a singleton
    def has_add_permission(self, request):
        return not SiteProfile.objects.exists()
    

# Register models FOR SERVICE MANAGEMENT here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)



# Register models FOR CERTIFICATE MANAGEMENT here.
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'issuer', 'issue_date', 'category')
    list_filter = ('category', 'issue_date')
    search_fields = ('title', 'issuer', 'description')

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'completion_date')
    list_filter = ('completion_date',)
    search_fields = ('title', 'description')


# Register models FOR PROJECT MANAGEMENT here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "timeline", "role")
    list_filter = ("is_featured",)
    list_editable = ("is_featured",)
    search_fields = ("title", "technologies")



# Register models FOR SKILL MANAGEMENT here.
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "level", "rating", "order")
    list_filter = ("category", "level")
    search_fields = ("title",)
    list_editable = ("order",)

@admin.register(SkillSummary)
class SkillSummaryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SkillSummary.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False

# Register models FOR CONTACT MANAGEMENT here.
@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "submitted_at")
    list_filter = ("submitted_at",)
    search_fields = ("name", "email", "subject")
    readonly_fields = ("submitted_at",)


 # Register models FOR EMAIL TEMPLATE MANAGEMENT here.
@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_type", "subject")
    list_filter = ("template_type",)



# Register models FOR USER PROFILE MANAGEMENT here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "get_email")
    search_fields = ("name", "title")
    
    @admin.display(description='Email')
    def get_email(self, obj):
        # Get the first email contact detail
        email_contact = obj.contact_details.filter(contact_type='email').first()
        return email_contact.value if email_contact else 'No email'


# Register models FOR RESUME MANAGEMENT here.
@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title", "summary")


# Register models FOR SOCIAL PROFILE MANAGEMENT here.
@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = ("platform", "handle", "followers")
    list_filter = ("platform",)
    search_fields = ("platform", "handle")


# Register models FOR DETAILED PROFILE MANAGEMENT here.
@admin.register(ContactDetail)
class ContactDetailAdmin(admin.ModelAdmin):
    list_display = ('profile', 'contact_type', 'value', 'order')
    list_editable = ('order',)
    list_filter = ('contact_type',)


#   Register models FOR EDUCATION MANAGEMENT here.
@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'degree', 'profile', 'start_date', 'end_date')
    list_filter = ('profile',)


# Register models FOR PROFESSIONAL EXPERIENCE MANAGEMENT here.
@admin.register(ProfessionalExperience)
class ProfessionalExperienceAdmin(admin.ModelAdmin):
    list_display = ('company', 'position', 'profile', 'start_date', 'end_date')
    list_filter = ('profile',)
    search_fields = ('company', 'position')


# Register models FOR BACKGROUND INTEREST MANAGEMENT here.
@admin.register(BackgroundInterest)
class BackgroundInterestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'profile', 'order')
    list_editable = ('order',)
    list_filter = ('category', 'profile')


# Register models FOR PROFESSIONAL PHILOSOPHY MANAGEMENT here.
@admin.register(ProfessionalPhilosophy)
class ProfessionalPhilosophyAdmin(admin.ModelAdmin):
    list_display = ('profile', 'quote_preview')
    search_fields = ('profile__name', 'quote')
    
    @admin.display(description='Quote Preview')
    def quote_preview(self, obj):
        return obj.quote[:100] + '...' if len(obj.quote) > 100 else obj.quote


# Register models FOR PROFILE DETAIL MANAGEMENT here.   
@admin.register(ProfileDetail)
class ProfileDetailAdmin(admin.ModelAdmin):
    list_display = ('profile', 'detail_type', 'value', 'order')
    list_editable = ('order',)
    list_filter = ('detail_type', 'profile')

# Register models FOR SOCIAL PLATFORM MANAGEMENT here.
@admin.register(SocialPlatform)
class SocialPlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "followers")
    list_filter  = ("category",)
    search_fields= ("name",)



# Register models FOR EMAIL TEMPLATE MANAGEMENT here.
# @admin.register(EmailTemplate)
# class EmailTemplateAdmin(admin.ModelAdmin):
#     list_display = ("template_type", "subject")
#     list_filter = ("template_type",)


class GuidelineItemInline(admin.TabularInline):
    model = GuidelineItem
    extra = 1

@admin.register(GuidelineSection)
class GuidelineSectionAdmin(admin.ModelAdmin):
    inlines = [GuidelineItemInline]

admin.site.register(EmailAddress)
admin.site.register(EmailTemplates)
admin.site.register(SecurityItem)
admin.site.register(Method)
admin.site.register(FAQ)
