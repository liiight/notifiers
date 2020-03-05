from datetime import datetime
from enum import Enum
from typing import Dict
from typing import List
from urllib.parse import urljoin

from pydantic import Field
from pydantic import root_validator
from pydantic.json import isoformat

from ..exceptions import ResourceError
from ..models.provider import Provider
from ..models.provider import ProviderResource
from ..models.provider import SchemaModel
from ..models.response import Response
from ..utils import requests


class Impact(Enum):
    critical = "critical"
    major = "major"
    minor = "minor"
    maintenance = "maintenance"
    none = "none"


class IncidentStatus(Enum):
    postmortem = "postmortem"
    investigating = "investigating"
    identified = "identified"
    resolved = "resolved"
    update = "update"
    scheduled = "scheduled"
    in_progress = "in_progress"
    verifying = "verifying"
    monitoring = "monitoring"
    completed = "completed"


class ComponentStatus(Enum):
    operational = "operational"
    under_maintenance = "under_maintenance"
    degraded_performance = "degraded_performance"
    partial_outage = "partial_outage"
    major_outage = "major_outage"
    empty = ""


class StatuspageBaseSchema(SchemaModel):
    api_key: str = Field(..., description="Authentication token")
    page_id: str = Field(..., description="Paged ID")


class StatuspageSchema(StatuspageBaseSchema):
    """Statuspage incident creation schema"""

    message: str = Field(..., description="Incident Name", alias="name")
    status: IncidentStatus = Field(None, description="Incident status")
    impact_override: Impact = Field(
        None, description="Value to override calculated impact value"
    )
    scheduled_for: datetime = Field(
        None, description="The timestamp the incident is scheduled for"
    )
    scheduled_until: datetime = Field(
        None, description="The timestamp the incident is scheduled until"
    )
    scheduled_remind_prior: bool = Field(
        None,
        description="Controls whether to remind subscribers prior to scheduled incidents",
    )
    scheduled_auto_in_progress: bool = Field(
        None,
        description="Controls whether the incident is scheduled to automatically change to in progress",
    )
    scheduled_auto_completed: bool = Field(
        None,
        description="Controls whether the incident is scheduled to automatically change to complete",
    )
    metadata: dict = Field(
        None,
        description="Attach a json object to the incident. All top-level values in the object must also be objects",
    )
    deliver_notifications: bool = Field(
        None,
        description="Deliver notifications to subscribers if this is true. If this is false, "
        "create an incident without notifying customers",
    )
    auto_transition_deliver_notifications_at_end: bool = Field(
        None,
        description="Controls whether send notification when scheduled maintenances auto transition to completed",
    )
    auto_transition_deliver_notifications_at_start: bool = Field(
        None,
        description="Controls whether send notification when scheduled maintenances auto transition to started",
    )
    auto_transition_to_maintenance_state: bool = Field(
        None,
        description="Controls whether send notification when scheduled maintenances auto transition to in progress",
    )
    auto_transition_to_operational_state: bool = Field(
        None,
        description="Controls whether change components status to operational once scheduled maintenance completes",
    )
    auto_tweet_at_beginning: bool = Field(
        None,
        description="Controls whether tweet automatically when scheduled maintenance starts",
    )
    auto_tweet_on_completion: bool = Field(
        None,
        description="Controls whether tweet automatically when scheduled maintenance completes",
    )
    auto_tweet_on_creation: bool = Field(
        None,
        description="Controls whether tweet automatically when scheduled maintenance is created",
    )
    auto_tweet_one_hour_before: bool = Field(
        None,
        description="Controls whether tweet automatically one hour before scheduled maintenance starts",
    )
    backfill_date: datetime = Field(
        None, description="TimeStamp when incident was backfilled"
    )
    backfilled: bool = Field(
        None,
        description="Controls whether incident is backfilled. If true, components cannot be specified",
    )
    body: str = Field(
        None, description="The initial message, created as the first incident update"
    )
    components: Dict[str, ComponentStatus] = Field(
        None, description="Map of status changes to apply to affected components"
    )
    component_ids: List[str] = Field(
        None, description="List of component_ids affected by this incident"
    )
    scheduled_auto_transition: bool = Field(
        None,
        description="Same as 'scheduled_auto_transition_in_progress'. Controls whether the incident is "
        "scheduled to automatically change to in progress",
    )

    @root_validator
    def values_dependencies(cls, values):
        backfill_values = [values.get(v) for v in ("backfill_date", "backfilled")]
        scheduled_values = [values.get(v) for v in ("scheduled_for", "scheduled_until")]

        if any(backfill_values) and not all(backfill_values):
            raise ValueError(
                "Cannot set just one of 'backfill_date' and 'backfilled', both need to be set"
            )
        if any(scheduled_values) and not all(scheduled_values):
            raise ValueError(
                "Cannot set just one of 'scheduled_for' and 'scheduled_until', both need to be set"
            )
        if any(
            values.get(v)
            for v in (
                "scheduled_until",
                "scheduled_remind_prior",
                "scheduled_auto_in_progress",
                "scheduled_auto_completed",
            )
        ) and not values.get("scheduled_for"):
            raise ValueError(
                "'scheduled_for' must be set when setting scheduled attributes"
            )
        if any(backfill_values) and any(scheduled_values):
            raise ValueError(
                "Cannot set both backfill attributes and scheduled attributes"
            )
        if any(backfill_values) and values.get("status"):
            raise ValueError("Cannot set 'status' when setting 'backfill'")
        return values

    class Config:
        json_encoders = {datetime: isoformat}


class StatuspageMixin:
    """Shared resources between :class:`Statuspage` and :class:`StatuspageComponents`"""

    base_url = "https://api.statuspage.io/v1/pages/{page_id}/"
    name = "statuspage"
    path_to_errors = ("error",)
    site_url = "https://statuspage.io"

    @staticmethod
    def request_headers(api_key: str) -> dict:
        return {"Authorization": f"OAuth {api_key}"}


class StatuspageComponents(StatuspageMixin, ProviderResource):
    """Return a list of Statuspage components for the page ID"""

    resource_name = components_url = "components"

    schema_model = StatuspageBaseSchema

    def _get_resource(self, data: StatuspageBaseSchema) -> dict:
        url = urljoin(self.base_url.format(page_id=data.page_id), self.components_url)
        headers = self.request_headers(data.api_key)
        response, errors = requests.get(
            url, headers=headers, path_to_errors=self.path_to_errors
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

    incidents_url = "incidents"

    _resources = {"components": StatuspageComponents()}

    schema_model = StatuspageSchema

    def _send_notification(self, data: StatuspageSchema) -> Response:
        url = urljoin(self.base_url.format(page_id=data.page_id), self.incidents_url)
        headers = self.request_headers(data.api_key)
        data_dict = data.to_dict(exclude={"page_id", "api_key"})
        payload = {"incident": data_dict}
        response, errors = requests.post(
            url, json=payload, headers=headers, path_to_errors=self.path_to_errors
        )
        return self.create_response(data_dict, response, errors)
