import json
import os
from typing import List

from core_layer.handler.notification_template_handler import NotificationTemplateHandler
from core_layer.model.notification_model import NotificationTemplate


class MockNotificationTemplateHandler(NotificationTemplateHandler):

    _templates: List[NotificationTemplate]

    def __init__(self) -> None:
        file_name = "message_templates.json"
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, file_name)
        with open(file_path, encoding="utf-8") as templates_file:
            self._templates = json.load(templates_file)

    def get_notification_template(self, notification_type: str, message_type: str, content_type: str, language: str = "de") -> NotificationTemplate:

        template = NotificationTemplate()
        template.content = self._templates[notification_type][message_type][content_type][language]

        return template
