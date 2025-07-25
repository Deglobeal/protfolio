from django.contrib import admin
from .models import Project, Certificate, Skill

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}  # Optional: if you add a slug field

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'issued_by', 'date_issued')
    list_filter = ('date_issued',)
    search_fields = ('title', 'issued_by')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'icon_class')
    list_editable = ('level',)