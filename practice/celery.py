from __future__ import absolute_import, unicode_literals
import os

# Set Django settings first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practice.settings")

# Initialize Django
import django
django.setup()

# Then create Celery app and import models
from celery import Celery
from celery.schedules import crontab
from django_celery_beat.models import PeriodicTask, IntervalSchedule

app = Celery("practice")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practice.settings")

# app = Celery("practice")
# app.config_from_object("django.conf:settings", namespace="CELERY")

# app.autodiscover_tasks()

# # Celery Beat Scheduler
# from celery.schedules import crontab
# from django_celery_beat.models import PeriodicTask, IntervalSchedule

