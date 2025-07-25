from django.db import models
from django.urls import reverse

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/')
    url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('project_detail', args=[str(self.id)])

class Certificate(models.Model):
    title = models.CharField(max_length=200)
    issued_by = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_issued = models.DateField()
    certificate_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='certificates/')
    
    def __str__(self):
        return self.title

class Skill(models.Model):
    name = models.CharField(max_length=100)
    level = models.IntegerField()
    icon_class = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    
    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"