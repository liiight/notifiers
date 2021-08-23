from ..core import Provider
from ..core import Response
from ..utils import requests


class VictorOps(Provider):
    """Send VictorOps webhook notifications"""

    base_url = "https://portal.victorops.com/ui/{ORGANIZATION_ID}/incidents"
    site_url = "https://portal.victorops.com/dash/{ORGANIZATION_ID}#/advanced/rest"
    name = "victorops"

    _required = {
        "required": [
            "rest_url",
            "message_type",
            "entity_id",
            "entity_display_name",
            "message",
        ]
    }
    _schema = {
        "type": "object",
        "properties": {
            "rest_url": {
                "type": "string",
                "format": "uri",
                "title": "the REST URL to use with routing_key. create one in victorops `integrations` tab.",
            },
            "message_type": {
                "type": "string",
                "title": "severity level can be: "
                "- critical or warning: Triggers an incident "
                "- acknowledgement: sends Acknowledgment to an incident "
                "- info: Creates a timeline event but doesn't trigger an incident "
                "- recovery or ok: Resolves an incident",
                "enum": [
                    "critical",
                    "warning",
                    "acknowledgement",
                    "info",
                    "recovery",
                    "ok",
                ],
            },
            "entity_id": {
                "type": "string",
                "title": "Unique id for the incident for aggregation ,Acknowledging, or resolving.",
            },
            "entity_display_name": {
                "type": "string",
                "title": "Display Name in the UI and Notifications.",
            },
            "message": {
                "type": "string",
                "title": "This is the description that will be posted in the incident.",
            },
            "annotations": {
                "type": "object",
                "patternProperties": {
                    "^vo_annotate.u.": {"type": "string"},
                    "^vo_annotate.s.": {"type": "string"},
                    "^vo_annotate.i.": {"type": "string"},
                },
                "minProperties": 1,
                "title": "annotations can be of three types: "
                "vo_annotate.u.{custom_name}, "
                "vo_annotate.s.{custom_name}, "
                "vo_annotate.i.{custom_name} .",
                "additionalProperties": False,
            },
            "additional_keys": {
                "type": "object",
                "title": "any additional keys that can be passed in the body",
            },
        },
        "additionalProperties": False,
    }

    def _prepare_data(self, data: dict) -> dict:
        annotations = data.pop("annotations", {})
        for annotation, value in annotations.items():
            data[annotation] = value

        additional_keys = data.pop("additional_keys", {})
        for additional_key, value in additional_keys.items():
            data[additional_key] = value
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop("rest_url")
        response, errors = requests.post(url, json=data)
        return self.create_response(data, response, errors)
