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
            "state_message",
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
                "- CRITICAL or WARNING: Triggers an incident "
                "- ACKNOWLEDGEMENT: Acks an incident "
                "- INFO: Creates a timeline event but doesn't trigger an incident "
                "- RECOVERY: Resolves an incident",
            },
            "entity_id": {
                "type": "string",
                "title": "Unique id for the incident for aggregation ,acking, or resolving.",
            },
            "entity_display_name": {
                "type": "string",
                "title": "Display Name in the UI and Notifications.",
            },
            "state_message": {
                "type": "string",
                "title": "This is the description that will be posted in the incident.",
            },
            "annotations": {
                "type": "object",
                "format": "{'annotation_type': 'annotation'}",
                "title": "annotations can be of three types vo_annotate.u.Runbook, vo_annotate.s.Note, "
                "vo_annotate.i.image.",
            },
            "additional_keys": {
                "type": "object",
                "title": "any additional keys that ca be passed in the body",
            },
        },
        "additionalProperties": False,
    }

    def _prepare_data(self, data: dict) -> dict:
        if data.get("annotations"):
            annotations = data.pop("annotations")
            for annotation in annotations:
                data[annotation] = annotations[annotation]

            if data.get("additional_keys"):
                additional_keys = data.pop("additional_keys")
                for additional_key in additional_keys:
                    data[additional_key] = additional_keys[additional_key]
        return data

    def _send_notification(self, data: dict) -> Response:
        url = data.pop("rest_url")
        response, errors = requests.post(url, json=data)
        return self.create_response(data, response, errors)
