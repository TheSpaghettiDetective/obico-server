from __future__ import absolute_import, unicode_literals
import os
import celery
import raven
from raven.contrib.celery import register_signal, register_logger_signal

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

class MyCelery(celery.Celery):

    def on_configure(self):
        if os.environ.get('SENTRY_DSN'):
            client = raven.Client(os.environ.get('SENTRY_DSN'))

            # register a custom filter to filter out duplicate logs
            register_logger_signal(client)

            # hook into the Celery error handler
            register_signal(client)

celery_app = MyCelery('config')
celery_app.conf.task_ignore_result = True
celery_app.conf.task_store_errors_even_if_ignored = True
celery_app.conf.broker_transport_options = {'visibility_timeout': 3600*12}
celery_app.conf.task_routes = {
    'app.tasks.print_notification': {'queue': 'realtime'},
    'app.tasks.process_print_events': {'queue': 'realtime'},
    'app.tasks.service_webhook': {'queue': 'realtime'},
    'app_ent.tasks.credit_dh_for_contribution': {'queue': 'realtime'},
    'app_ent.tasks.process_print_events_ent': {'queue': 'realtime'},
    'app_ent.tasks.send_welcome_email': {'queue': 'realtime'},
    'app_ent.tasks.set_coturn_credential': {'queue': 'realtime'},
    'app_ent.tasks.send_free_trial_expiring_message': {'queue': 'realtime'},
}

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()
