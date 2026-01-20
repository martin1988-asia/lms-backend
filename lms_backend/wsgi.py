"""
WSGI config for lms_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'lms_backend' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_backend.settings')

application = get_wsgi_application()
