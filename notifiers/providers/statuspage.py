from ..core import Provider
from ..core import ProviderResource
from ..core import Response
from ..exceptions import BadArguments
from ..exceptions import ResourceError
from ..utils import requests


class StatuspageMixin:
    """Shared resources between :class:`Statuspage` and :class:`StatuspageComponents`"""

    base_url = "https://api.statuspage.io/v1//pages/{page_id}/"
    name = "statuspage"
    path_to_errors = ("error",)
    site_url = "https://statuspage.io"


class StatuspageComponents(StatuspageMixin, ProviderResource):
    """Return a list of Statuspage components for the page ID"""

    resource_name = "components"
    components_url = "components.json"

    _required = {"required": ["api_key", "page_id"]}

    _schema = {
        "type": "object",
        "properties": {
            "api_key": {"type": "string", "title": "OAuth2 token"},
            "page_id": {"type": "string", "title": "Page ID"},
        },
        "additionalProperties": False,
    }

    def _get_resource(self, data: dict) -> dict:
        url = self.base_url.format(page_id=data["page_id"]) + self.components_url
        params = {"api_key": data.pop("api_key")}
        response, errors = requests.get(
            url, params=params, path_to_errors=self.path_to_errors
        )
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

    realtime_statuses = ["investigating", "identified", "monitoring", "resolved"]

    scheduled_statuses = ["scheduled", "in_progress", "verifying", "completed"]

    __component_ids = {
        "type": "array",
        "items": {"type": "string"},
        "title": "List of components whose subscribers should be notified (only applicable for pages with "
        "component subscriptions enabled)",
    }

    _required = {"required": ["message", "api_key", "page_id"]}

    _schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string", "title": "The name of the incident"},
            "api_key": {"type": "string", "title": "OAuth2 token"},
            "page_id": {"type": "string", "title": "Page ID"},
            "status": {
                "type": "string",
                "title": "Status of the incident",
                "enum": realtime_statuses + scheduled_statuses,
            },
            "body": {
                "type": "string",
                "title": "The initial message, created as the first incident update",
            },
            "wants_twitter_update": {
                "type": "boolean",
                "title": "Post the new incident to twitter",
            },
            "impact_override": {
                "type": "string",
                "title": "Override calculated impact value",
                "enum": ["none", "minor", "major", "critical"],
            },
            "component_ids": __component_ids,
            "deliver_notifications": {
                "type": "boolean",
                "title": "Control whether notifications should be delivered for the initial incident update",
            },
            "scheduled_for": {
                "type": "string",
                "format": "iso8601",
                "title": "Time the scheduled maintenance should begin",
            },
            "scheduled_until": {
                "type": "string",
                "format": "iso8601",
                "title": "Time the scheduled maintenance should end",
            },
            "scheduled_remind_prior": {
                "type": "boolean",
                "title": "Remind subscribers 60 minutes before scheduled start",
            },
            "scheduled_auto_in_progress": {
                "type": "boolean",
                "title": "Automatically transition incident to 'In Progress' at start",
            },
            "scheduled_auto_completed": {
                "type": "boolean",
                "title": "Automatically transition incident to 'Completed' at end",
            },
            "backfilled": {"type": "boolean", "title": "Create an historical incident"},
            "backfill_date": {
                "format": "date",
                "type": "string",
                "title": "Date of incident in YYYY-MM-DD format",
            },
        },
        "dependencies": {
            "backfill_date": ["backfilled"],
            "backfilled": ["backfill_date"],
            "scheduled_for": ["scheduled_until"],
            "scheduled_until": ["scheduled_for"],
            "scheduled_remind_prior": ["scheduled_for"],
            "scheduled_auto_in_progress": ["scheduled_for"],
            "scheduled_auto_completed": ["scheduled_for"],
        },
        "additionalProperties": False,
    }

    def _validate_data_dependencies(self, data: dict) -> dict:
        scheduled_properties = [prop for prop in data if prop.startswith("scheduled")]
        scheduled = any(data.get(prop) is not None for prop in scheduled_properties)

        backfill_properties = [prop for prop in data if prop.startswith("backfill")]
        backfill = any(data.get(prop) is not None for prop in backfill_properties)

        if scheduled and backfill:
            raise BadArguments(
                provider=self.name,
                validation_error="Cannot set both 'backfill' and 'scheduled' incident properties "
                "in the same notification!",
            )

        status = data.get("status")
        if scheduled and status and status not in self.scheduled_statuses:
            raise BadArguments(
                provider=self.name,
                validation_error=f"Status '{status}' is a realtime incident status! "
                f"Please choose one of {self.scheduled_statuses}",
            )
        elif backfill and status:
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
                value = "t" if value else "f"
            new_data[f"incident[{key}]"] = value
        return new_data

    def _send_notification(self, data: dict) -> Response:
        url = self.base_url.format(page_id=data.pop("page_id")) + self.incidents_url
        params = {"api_key": data.pop("api_key")}
        response, errors = requests.post(
            url, data=data, params=params, path_to_errors=self.path_to_errors
        )
        return self.create_response(data, response, errors)
