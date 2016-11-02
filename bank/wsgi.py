"""
WSGI config for bank project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys

sys.path.insert(0, '/opt/python/current/app')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bank.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
