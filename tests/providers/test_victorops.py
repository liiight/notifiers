import os

import pytest

provider = "victorops"


class TestVicrotops:
    """
    Victorops rest alert tests
    Online test rely on setting the env variable VICTOROPS_REST_URL
    """

    @pytest.mark.online
    def test_all_options(self, provider):
        VICTOROPS_REST_URL = os.getenv("VICTOROPS_REST_URL")
        data = {
            "rest_url": VICTOROPS_REST_URL,
            "message_type": "CRITICAL",
            "entity_id": "BA tesing",
            "entity_display_name": "messege test header",
            "message": "text in body",
            "annotations": {
                "vo_annotate.i.Graph": "https://shorturl.at/dAQ28",
                "vo_annotate.s.Note": "'You can't have everything. Where would you put it?' Steven Wright",
                "vo_annotate.u.Runbook": "https://giphy.com/gifs/win-xNBcChLQt7s9a/fullscreen",
            },
            "additional_keys": {
                "foo": "custom fields",
                "monitoring_tool": "official victorops fields",
            },
        }
        rsp = provider.notify(**data)
        assert rsp.ok
        assert rsp.status == "Success"
        assert rsp.errors is None
