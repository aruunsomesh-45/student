"""
WSGI config for mindset_platform project.

Exposes WSGI callable as a module-level variable named `application`.
Configures WhiteNoise directly at the WSGI level for static file serving.
Ensures database migrations and seed records are automatically applied on server boot.
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindset_platform.settings')

BASE_DIR = Path(__file__).resolve().parent.parent

# Base Django WSGI application
application = get_wsgi_application()

# Run database migrations and site setup automatically on boot
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    
    # Auto-provision Site record for allauth
    from django.contrib.sites.models import Site
    Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': os.getenv('RAILWAY_PUBLIC_DOMAIN', 'web-production-a7c4d.up.railway.app'),
            'name': 'MindConnect'
        }
    )

    # Auto-seed question bank if empty
    from apps.assessments.models import Question
    if Question.objects.count() == 0:
        call_command('seed_questions')
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f"WSGI startup initialization notice: {e}")

# Wrap with WhiteNoise to guarantee static files are served in production
staticfiles_dir = BASE_DIR / 'staticfiles'
if not staticfiles_dir.exists():
    staticfiles_dir.mkdir(parents=True, exist_ok=True)

application = WhiteNoise(application, root=str(staticfiles_dir), prefix='/static/')

static_source_dir = BASE_DIR / 'static'
if static_source_dir.exists():
    application.add_files(str(static_source_dir), prefix='static/')
