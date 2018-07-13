from __future__ import absolute_import

import os
from celery import Celery



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lz_jarvis.settings')

app = Celery('lz_jarvis')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

"""
# Cron example

from celery.schedules import crontab

app.conf.beat_schedule = {
    'reporte_usuario': {
        'task': 'read_file.tasks.reporte_usuario',
        'schedule': crontab(minute='*/1')
    }
}
"""
