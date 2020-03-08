from datetime import datetime
from enum import Enum
from typing import List

from pydantic import constr
from pydantic import Field
from pydantic import HttpUrl
from pydantic import validator

from ..models.provider import Provider
from ..models.provider import ResourceSchema
from ..models.response import Response
from ..utils import requests


class HttpsUrl(HttpUrl):
    allowed_schemes = ("https",)


class PagerDutyLink(ResourceSchema):
    href: HttpUrl = Field(..., description="URL of the link to be attached.")
    text: str = Field(
        ...,
        description="Plain text that describes the purpose of the link, and can be used as the link's text",
    )


class PagerDutyImage(ResourceSchema):
    src: HttpsUrl = Field(
        ...,
        description="The source of the image being attached to the incident. This image must be served via HTTPS.",
    )
    href: HttpUrl = Field(
        None, description="Optional URL; makes the image a clickable link."
    )
    alt: str = Field(None, description="Optional alternative text for the image.")


class PagerDutyPayloadSeverity(Enum):
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class PagerDutyEventAction(Enum):
    trigger = "trigger"
    acknowledge = "acknowledge"
    resolve = "resolve"


class PagerDutyPayload(ResourceSchema):
    message: constr(max_length=1024) = Field(
        ...,
        description="A brief text summary of the event,"
        " used to generate the summaries/titles of any associated alerts.",
        alias="summary",
    )
    source: str = Field(
        ...,
        description="The unique location of the affected system, preferably a hostname or FQDN",
    )
    severity: PagerDutyPayloadSeverity = Field(
        ...,
        description="The perceived severity of the status the event is describing with respect to the affected system",
    )
    timestamp: datetime = Field(
        None,
        description="The time at which the emitting tool detected or generated the event",
    )
    component: str = Field(
        None,
        description="Component of the source machine that is responsible for the event, for example mysql or eth0",
    )
    group: str = Field(
        None,
        description="Logical grouping of components of a service, for example app-stack",
    )
    class_: str = Field(
        None,
        description="The class/type of the event, for example ping failure or cpu load",
        alias="class",
    )
    custom_details: dict = Field(
        None, description="Additional details about the event and affected system"
    )

    @validator("timestamp")
    def to_timestamp(cls, v: datetime):
        return v.timestamp()

    class Config:
        json_encoders = {PagerDutyPayloadSeverity: lambda v: v.value}
        allow_population_by_field_name = True


class PagerDutySchema(ResourceSchema):
    routing_key: constr(min_length=32, max_length=32) = Field(
        ...,
        description="This is the 32 character Integration Key for an integration on a service or on a global ruleset",
    )
    event_action: PagerDutyEventAction = Field(..., description="The type of event")
    dedup_key: constr(max_length=255) = Field(
        None, description="Deduplication key for correlating triggers and resolves"
    )
    payload: PagerDutyPayload
    images: List[PagerDutyImage] = Field(None, description="List of images to include")
    links: List[PagerDutyLink] = Field(None, description="List of links to include")

    class Config:
        json_encoders = {PagerDutyEventAction: lambda v: v.value}


class PagerDuty(Provider):
    """Send PagerDuty Events"""

    name = "pagerduty"
    base_url = "https://events.pagerduty.com/v2/enqueue"
    site_url = "https://v2.developer.pagerduty.com/"
    path_to_errors = ("errors",)

    schema_model = PagerDutySchema

    def _send_notification(self, data: PagerDutySchema) -> Response:
        url = self.base_url
        response, errors = requests.post(
            url, json=data.to_dict(), path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
