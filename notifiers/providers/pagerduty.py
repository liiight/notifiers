from __future__ import annotations

from typing import Any, Literal

from pydantic import ConfigDict, Field

from ..core import Provider, Response
from ..models import ISO8601Datetime, SchemaModel
from ..utils import requests


class PagerDutyImage(SchemaModel):
    src: str = Field(description="The source of the image being attached to the incident. This image must be served via HTTPS.")
    href: str | None = Field(None, description="Optional URL; makes the image a clickable link")
    alt: str | None = Field(None, description="Optional alternative text for the image")


class PagerDutyLink(SchemaModel):
    href: str = Field(description="URL of the link to be attached")
    text: str = Field(description="Plain text that describes the purpose of the link, and can be used as the link's text")


class PagerDutySchema(SchemaModel):
    # Unknown arguments are passed through to the API
    model_config = ConfigDict(extra="allow")

    routing_key: str = Field(
        description='The GUID of one of your Events API V2 integrations. This is the "Integration Key" listed on the Events API V2 integration\'s detail page',
    )
    event_action: Literal["trigger", "acknowledge", "resolve"] = Field(description="The type of event")
    source: str = Field(description="The unique location of the affected system, preferably a hostname or FQDN")
    severity: Literal["critical", "error", "warning", "info"] = Field(
        description="The perceived severity of the status the event is describing with respect to the affected system",
    )
    message: str = Field(description="A brief text summary of the event, used to generate the summaries/titles of any associated alerts")
    dedup_key: str | None = Field(None, max_length=255, description="Deduplication key for correlating triggers and resolves")
    timestamp: ISO8601Datetime | None = Field(None, description="The time at which the emitting tool detected or generated the event in ISO 8601")
    component: str | None = Field(None, description="Component of the source machine that is responsible for the event")
    group: str | None = Field(None, description="Logical grouping of components of a service")
    class_: str | None = Field(None, alias="class", description="The class/type of the event")
    custom_details: dict[str, Any] | None = Field(None, description="Additional details about the event and affected system")
    images: list[PagerDutyImage] | None = Field(None, description="List of images to include")
    links: list[PagerDutyLink] | None = Field(None, description="List of links to include")


class PagerDuty(Provider):
    """Send PagerDuty Events"""

    name = "pagerduty"
    base_url = "https://events.pagerduty.com/v2/enqueue"
    site_url = "https://v2.developer.pagerduty.com/"
    path_to_errors = ("errors",)

    __payload_attributes = [
        "message",
        "source",
        "severity",
        "timestamp",
        "component",
        "group",
        "class",
        "custom_details",
    ]

    schema_model = PagerDutySchema

    def _prepare_data(self, data: dict) -> dict:
        payload = {attribute: data.pop(attribute) for attribute in self.__payload_attributes if data.get(attribute)}
        payload["summary"] = payload.pop("message")
        data["payload"] = payload
        return data

    def _send_notification(self, data: dict) -> Response:
        url = self.base_url
        response, errors = requests.post(url, json=data, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)
