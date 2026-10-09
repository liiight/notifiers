from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from ..core import Provider, ProviderResource, Response
from ..exceptions import BadArguments, ResourceError
from ..models import DateString, ISO8601Datetime, SchemaModel
from ..utils import requests

REALTIME_STATUSES = ["investigating", "identified", "monitoring", "resolved"]
SCHEDULED_STATUSES = ["scheduled", "in_progress", "verifying", "completed"]


class StatuspageComponentsSchema(SchemaModel):
    api_key: str = Field(description="OAuth2 token")
    page_id: str = Field(description="Page ID")


class StatuspageSchema(SchemaModel):
    message: str = Field(description="The name of the incident")
    api_key: str = Field(description="OAuth2 token")
    page_id: str = Field(description="Page ID")
    status: Literal["investigating", "identified", "monitoring", "resolved", "scheduled", "in_progress", "verifying", "completed"] | None = Field(
        None, description="Status of the incident"
    )
    body: str | None = Field(None, description="The initial message, created as the first incident update")
    wants_twitter_update: bool | None = Field(None, description="Post the new incident to twitter")
    impact_override: Literal["none", "minor", "major", "critical"] | None = Field(None, description="Override calculated impact value")
    component_ids: list[str] | None = Field(
        None,
        description="List of components whose subscribers should be notified (only applicable for pages with component subscriptions enabled)",
    )
    deliver_notifications: bool | None = Field(None, description="Control whether notifications should be delivered for the initial incident update")
    scheduled_for: ISO8601Datetime | None = Field(None, description="Time the scheduled maintenance should begin")
    scheduled_until: ISO8601Datetime | None = Field(None, description="Time the scheduled maintenance should end")
    scheduled_remind_prior: bool | None = Field(None, description="Remind subscribers 60 minutes before scheduled start")
    scheduled_auto_in_progress: bool | None = Field(None, description="Automatically transition incident to 'In Progress' at start")
    scheduled_auto_completed: bool | None = Field(None, description="Automatically transition incident to 'Completed' at end")
    backfilled: bool | None = Field(None, description="Create an historical incident")
    backfill_date: DateString | None = Field(None, description="Date of incident in YYYY-MM-DD format")


class StatuspageMixin:
    """Shared resources between :class:`Statuspage` and :class:`StatuspageComponents`"""

    base_url = "https://api.statuspage.io/v1//pages/{page_id}/"
    name = "statuspage"
    path_to_errors = ("error",)
    site_url = "https://statuspage.io"

    @model_validator(mode="after")
    def _check_dependencies(self):
        self.require_dependencies(
            {
                "backfill_date": ["backfilled"],
                "backfilled": ["backfill_date"],
                "scheduled_for": ["scheduled_until"],
                "scheduled_until": ["scheduled_for"],
                "scheduled_remind_prior": ["scheduled_for"],
                "scheduled_auto_in_progress": ["scheduled_for"],
                "scheduled_auto_completed": ["scheduled_for"],
            }
        )
        return self


class StatuspageComponents(StatuspageMixin, ProviderResource):
    """Return a list of Statuspage components for the page ID"""

    resource_name = "components"
    components_url = "components.json"

    schema_model = StatuspageComponentsSchema

    def _get_resource(self, data: dict) -> dict:
        url = self.base_url.format(page_id=data["page_id"]) + self.components_url
        params = {"api_key": data.pop("api_key")}
        response, errors = requests.get(url, params=params, path_to_errors=self.path_to_errors)
        if errors:
            raise ResourceError(
                errors=errors,
                resource=self.resource_name,
                provider=self.name,
                data=data,
                response=response,
            )
        return response.json()


class Statuspage(StatuspageMixin, Provider):
    """Create Statuspage incidents"""

    incidents_url = "incidents.json"

    _resources = {"components": StatuspageComponents()}

    realtime_statuses = REALTIME_STATUSES

    scheduled_statuses = SCHEDULED_STATUSES

    schema_model = StatuspageSchema

    def _validate_data_dependencies(self, data: dict) -> dict:
        scheduled_properties = [prop for prop in data if prop.startswith("scheduled")]
        scheduled = any(data.get(prop) is not None for prop in scheduled_properties)

        backfill_properties = [prop for prop in data if prop.startswith("backfill")]
        backfill = any(data.get(prop) is not None for prop in backfill_properties)

        if scheduled and backfill:
            raise BadArguments(
                provider=self.name,
                validation_error="Cannot set both 'backfill' and 'scheduled' incident properties in the same notification!",
            )

        status = data.get("status")
        if scheduled and status and status not in self.scheduled_statuses:
            raise BadArguments(
                provider=self.name,
                validation_error=f"Status '{status}' is a realtime incident status! Please choose one of {self.scheduled_statuses}",
            )
        if backfill and status:
            raise BadArguments(
                provider=self.name,
                validation_error="Cannot set 'status' when setting 'backfill'!",
            )

        return data

    def _prepare_data(self, data: dict) -> dict:
        new_data = {
            "incident[name]": data.pop("message"),
            "api_key": data.pop("api_key"),
            "page_id": data.pop("page_id"),
        }
        for key, value in data.items():
            if isinstance(value, bool):
                value = "t" if value else "f"  # noqa: PLW2901
            new_data[f"incident[{key}]"] = value
        return new_data

    def _send_notification(self, data: dict) -> Response:
        url = self.base_url.format(page_id=data.pop("page_id")) + self.incidents_url
        params = {"api_key": data.pop("api_key")}
        response, errors = requests.post(url, data=data, params=params, path_to_errors=self.path_to_errors)
        return self.create_response(data, response, errors)
