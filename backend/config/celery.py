from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('config')
celery_app.conf.task_ignore_result = True
celery_app.conf.task_store_errors_even_if_ignored = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.broker_transport_options = {'visibility_timeout': 3600*12}
celery_app.conf.task_routes = {
    'app.tasks.process_print_events': {'queue': 'realtime'},
    'app_ent.tasks.credit_dh_for_contribution': {'queue': 'realtime'},
    'app_ent.tasks.process_print_events_ent': {'queue': 'realtime'},
    'app_ent.tasks.setup_free_trial': {'queue': 'realtime'},
    'notifications.tasks.send_print_notifications': {'queue': 'realtime'},
}

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()
