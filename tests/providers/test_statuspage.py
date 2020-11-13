import datetime
import logging
import os
from time import sleep

import pytest
import requests

from notifiers.exceptions import BadArguments
from notifiers.exceptions import ResourceError
from notifiers.models.response import ResponseStatus

provider = "statuspage"

log = logging.getLogger("notifiers")


@pytest.fixture(autouse=True, scope="module")
def close_all_open_incidents(request):
    api_key = os.getenv("NOTIFIERS_STATUSPAGE_API_KEY")
    page_id = os.getenv("NOTIFIERS_STATUSPAGE_PAGE_ID")

    s = requests.Session()
    base_url = f"https://api.statuspage.io/v1/pages/{page_id}/incidents"
    s.headers = {"Authorization": f"OAuth {api_key}"}
    url = f"{base_url}/unresolved"
    incidents = s.get(url).json()
    for incident in incidents:
        incident_id = incident["id"]
        url = f"{base_url}/{incident_id}"
        log.debug("deleting status page incident %s", incident_id)
        s.delete(url)
        sleep(2)


class TestStatusPage:
    def test_errors(self, provider):
        data = {"api_key": "foo", "page_id": "foo", "message": "foo"}
        rsp = provider.notify(**data)
        assert rsp.status is ResponseStatus.FAILURE
        assert "Could not authenticate" in rsp.errors

    @pytest.mark.online
    @pytest.mark.parametrize(
        "data",
        [
            ({"message": "foo"}),
            (
                {
                    "message": "Test realitme",
                    "status": "investigating",
                    "body": "Incident body",
                    "impact_override": "minor",
                    "deliver_notifications": False,
                }
            ),
            (
                {
                    "message": "Test scheduled",
                    "status": "scheduled",
                    "body": "Incident body",
                    "impact_override": "minor",
                    "deliver_notifications": False,
                    "scheduled_for": (
                        datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                    ).isoformat(),
                    "scheduled_until": (
                        datetime.datetime.utcnow() + datetime.timedelta(minutes=12)
                    ).isoformat(),
                    "scheduled_remind_prior": False,
                    "scheduled_auto_in_progress": True,
                    "scheduled_auto_completed": True,
                }
            ),
            (
                {
                    "message": "Test backfill",
                    "body": "Incident body",
                    "impact_override": "minor",
                    "backfilled": True,
                    "backfill_date": datetime.datetime.now(),
                }
            ),
        ],
    )
    def test_success(self, data, provider):
        provider.notify(**data, raise_on_errors=True)


class TestStatuspageComponents:
    resource = "components"

    def test_statuspage_components_attribs(self, resource):
        assert resource.schema() == {
            "additionalProperties": False,
            "description": "The base class for Schemas",
            "properties": {
                "api_key": {
                    "description": "Authentication token",
                    "title": "Api Key",
                    "type": "string",
                },
                "page_id": {
                    "description": "Paged ID",
                    "title": "Page Id",
                    "type": "string",
                },
            },
            "required": ["api_key", "page_id"],
            "title": "StatuspageBaseSchema",
            "type": "object",
        }

        assert resource.name == provider
        assert resource.required == ["api_key", "page_id"]

    def test_statuspage_components_negative(self, resource):
        with pytest.raises(BadArguments):
            resource(env_prefix="foo")

        with pytest.raises(ResourceError, match="Could not authenticate"):
            resource(api_key="foo", page_id="bar")
