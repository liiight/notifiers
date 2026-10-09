from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_core import PydanticCustomError

from ..core import Provider, Response
from ..models import SchemaModel, Url
from ..utils import requests

ANNOTATION_KEY = re.compile(r"^vo_annotate\.[usi]\.")


class VictorOpsSchema(SchemaModel):
    rest_url: Url = Field(description="the REST URL to use with routing_key. create one in victorops `integrations` tab.")
    message_type: Literal["critical", "warning", "acknowledgement", "info", "recovery", "ok"] = Field(
        description="severity level can be: "
        "- critical or warning: Triggers an incident "
        "- acknowledgement: sends Acknowledgment to an incident "
        "- info: Creates a timeline event but doesn't trigger an incident "
        "- recovery or ok: Resolves an incident",
    )
    entity_id: str = Field(description="Unique id for the incident for aggregation ,Acknowledging, or resolving.")
    entity_display_name: str = Field(description="Display Name in the UI and Notifications.")
    message: str = Field(description="This is the description that will be posted in the incident.")
    annotations: dict[str, str] | None = Field(
        None,
        min_length=1,
        description="annotations can be of three types: vo_annotate.u.{custom_name}, vo_annotate.s.{custom_name}, vo_annotate.i.{custom_name} .",
    )
    additional_keys: dict[str, Any] | None = Field(None, description="any additional keys that can be passed in the body")

    @field_validator("annotations")
    @classmethod
    def _check_annotation_keys(cls, value: dict[str, str] | None) -> dict[str, str] | None:
        for key in value or {}:
            if not ANNOTATION_KEY.match(key):
                raise PydanticCustomError(
                    "annotation_key",
                    "'{key}' is not a valid annotation, must start with vo_annotate.u., vo_annotate.s. or vo_annotate.i.",
                    {"key": key},
                )
        return value


class VictorOps(Provider):
    """Send VictorOps webhook notifications"""

    base_url = "https://portal.victorops.com/ui/{ORGANIZATION_ID}/incidents"
    site_url = "https://portal.victorops.com/dash/{ORGANIZATION_ID}#/advanced/rest"
    name = "victorops"

    schema_model = VictorOpsSchema

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
