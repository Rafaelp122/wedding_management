"""
Celery configuration for Wedding Management project.

This module initializes Celery and automatically discovers tasks
in all installed Django apps.
"""

import os

from celery import Celery

# Set default Django settings module
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "wedding_management.settings.local"
)

app = Celery("wedding_management")

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    print(f"Request: {self.request!r}")
