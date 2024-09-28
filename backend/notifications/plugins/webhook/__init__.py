from typing import Dict, Optional, Any
import logging
import requests  # type: ignore
import io
import os
import json
from enum import IntEnum
import requests
from rest_framework.serializers import ValidationError
from datetime import datetime

from notifications.plugin import (
    BaseNotificationPlugin,
    FailureAlertContext,
    PrinterNotificationContext,
    TestMessageContext,
)

LOGGER = logging.getLogger(__name__)


class WebhookException(Exception):
    pass

class WebhookNotificationPlugin(BaseNotificationPlugin):

    def validate_config(self, data: Dict) -> Dict:
        if 'custom_webhook_URL' in data:
            custom_webhook_URL = data['custom_webhook_URL'].strip()
            return {'custom_webhook_URL': custom_webhook_URL}
        raise ValidationError('custom_webhook_URL is missing from config')

    def get_webhook_URL_from_config(self, config: Dict) -> str:
        if config and 'custom_webhook_URL' in config:
            return config['custom_webhook_URL']
        return ''

    def i(self, s: str) -> str:
        return f"<i>{s}</i>"

    def b(self, s: str):
        return f"<b>{s}</b>"

    def u(self, s: str):
        return f"<u>{s}</u>"

    def execute_webhook(
        self,
        url: str,
        eventData: Dict,
        timeout: float = 5.0,
    ) -> None:

        headers = {'content-type': 'application/json'}
        response = requests.post(url, json=eventData, headers=headers, timeout=timeout)
        response.raise_for_status()

    def send_failure_alert(self, context: FailureAlertContext) -> None:

        webhook_URL = self.get_webhook_URL_from_config(context.config)
        if not webhook_URL:
            return

        printer: Dict[str, Any] = {
            "id": context.printer.id,
            "name": context.printer.name,
        }

        printStart = ""
        if context.print.started_at is not None:  printStart = context.print.started_at.timestamp()
        printEnd = ""
        if context.print.ended_at is not None: printEnd = context.print.ended_at.timestamp()

        printJob: Dict[str, Any] = {
            "id": context.print.id,
            "filename": context.print.filename,
            "started_at": printStart,
            "ended_at": printEnd,
        }

        event: Dict[str, Any] = {
            "type": "PrintFailure",
            "is_warning": context.is_warning,
            "print_paused": context.print_paused,
        }

        data: Dict[str, Any] = {
            "event": event,
            "printer": printer,
            "print": printJob,
            "img_url": context.img_url,
        }

        try:
            self.execute_webhook(
                url=webhook_URL,
                eventData=data,
            )
        except:
            pass # Ignore errors on webhook failures

    def send_printer_notification(self, context: PrinterNotificationContext) -> None:

        webhook_URL = self.get_webhook_URL_from_config(context.config)
        if not webhook_URL:
            return

        event: Dict[str, Any] = {
            "type": context.notification_type,
        }

        printer: Dict[str, Any] = {
            "id": context.printer.id,
            "name": context.printer.name,
        }

        data: Dict[str, Any] = {
            "event": event,
            "printer": printer,
        }

        if context.print is not None:
            printStart = ""
            if context.print.started_at is not None:  printStart = context.print.started_at.timestamp()
            printEnd = ""
            if context.print.ended_at is not None: printEnd = context.print.ended_at.timestamp()

            printJob: Dict[str, Any] = {
                "id": context.print.id,
                "filename": context.print.filename,
                "started_at": printStart,
                "ended_at": printEnd,
            }

            data["print"] = printJob
            data["img_url"] = context.img_url

        try:
            self.execute_webhook(
                url=webhook_URL,
                eventData=data,
            )
        except:
            pass # Ignore errors on webhook failures

    def send_test_message(self, context: TestMessageContext) -> None:
        webhook_URL = self.get_webhook_URL_from_config(context.config)
        if not webhook_URL:
            return

        data: Dict[str, Any] = {
            "event": "TestEvent",
        }

        self.execute_webhook(
            url=webhook_URL,
            eventData=data,
        )


def __load_plugin__():
    return WebhookNotificationPlugin()
