"""
Settings package for Wedding Management project.

The settings are split into:
- base.py: Common settings for all environments
- local.py: Development settings (SQLite, DEBUG=True)
- production.py: Production settings (PostgreSQL, DEBUG=False)
- test.py: Test settings (in-memory database)

Usage:
    Set DJANGO_SETTINGS_MODULE environment variable:
    - Development: export DJANGO_SETTINGS_MODULE=wedding_management.settings.local
    - Production: export DJANGO_SETTINGS_MODULE=wedding_management.settings.production
    - Testing: export DJANGO_SETTINGS_MODULE=wedding_management.settings.test
"""

import os

# Default to local settings if not specified
settings_module = os.getenv(
    'DJANGO_SETTINGS_MODULE',
    'wedding_management.settings.local'
)

# Import the appropriate settings
if 'local' in settings_module:
    from .local import *
elif 'production' in settings_module:
    from .production import *
elif 'test' in settings_module:
    from .test import *
else:
    from .local import *
