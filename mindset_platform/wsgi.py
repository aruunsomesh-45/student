"""
WSGI config for mindset_platform project.

Exposes WSGI callable as a module-level variable named `application`.
Configures WhiteNoise directly at the WSGI level for static file serving.
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindset_platform.settings')

BASE_DIR = Path(__file__).resolve().parent.parent

# Base Django WSGI application
application = get_wsgi_application()

# Wrap with WhiteNoise to guarantee static files are served in production
staticfiles_dir = BASE_DIR / 'staticfiles'
if not staticfiles_dir.exists():
    staticfiles_dir.mkdir(parents=True, exist_ok=True)

application = WhiteNoise(application, root=str(staticfiles_dir), prefix='/static/')

static_source_dir = BASE_DIR / 'static'
if static_source_dir.exists():
    application.add_files(str(static_source_dir), prefix='static/')
