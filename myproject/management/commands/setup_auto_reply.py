from django.core.management.base import BaseCommand
from myapp.models import AutoReplyTemplate  # Replace 'myapp' with your app name

class Command(BaseCommand):
    help = 'Creates a default auto-reply template'

    def handle(self, *args, **options):
        template, created = AutoReplyTemplate.objects.get_or_create(
            name="Default Auto-Reply",
            defaults={
                'subject': "Thank you for contacting Gerard Ugwu",
                'message': """Hello {name},

Thank you for reaching out! I've received your message regarding "{subject}" and will review it carefully.

I typically respond within 24 hours. If your matter is urgent, feel free to call me at +2347032388531.

Here's a copy of your message for your records:
Subject: {subject}
Message: {message}

Looking forward to connecting with you!

Best regards,
Gerard Ugwu
Backend Developer
+2347032388531
kachimaxy1@gmail.com"""
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Default auto-reply template created!'))
        else:
            self.stdout.write(self.style.SUCCESS('Default auto-reply template already exists.'))