from pathlib import Path

from django.apps import AppConfig
from django.utils.autoreload import autoreload_started
from django.conf import settings


class NotificationsAppConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        if settings.DEBUG:
            autoreload_started.connect(add_plugins_to_watchdog)


def add_plugins_to_watchdog(sender, **kwargs):
    for p in Path(settings.BASE_DIR + '/notifications/plugins').iterdir():
        if p.is_dir() and Path(p / '__init__.py').exists():
            sender.watch_dir(p.absolute(), '*.py')
