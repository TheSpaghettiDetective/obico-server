"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
import newrelic.agent


newrelic.agent.initialize()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
application = SentryAsgiMiddleware(get_default_application())
