from django import forms
from .models import ContactSubmission, Certificate, Project, Skill, EmailTemplate

class ContactSubmissionForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = '__all__'

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = '__all__'

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = '__all__'
