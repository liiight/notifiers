import pytest

provider = "victorops"


class TestVicrotops:
    """
    Victorops rest alert tests
    Online test rely on setting the env variable VICTOROPS_REST_URL
    """

    @pytest.mark.skip("Skipping until obtaining a permanent key")
    @pytest.mark.online
    def test_all_options(self, provider):
        data = {
            "message_type": "info",
            "entity_id": "BA tesing",
            "entity_display_name": "message test header",
            "message": "text in body",
            "annotations": {
                "vo_annotate.i.Graph": "https://shorturl.at/dAQ28",
                "vo_annotate.s.Note": "'You can't have everything. Where would you put it?' Steven Wright",
                "vo_annotate.u.Runbook": "https://giphy.com/gifs/win-xNBcChLQt7s9a/fullscreen",
            },
            "additional_keys": {
                "foo": "this is a custom fields",
                "monitoring_tool": "this is an official victorops fields",
            },
        }
        rsp = provider.notify(**data)
        assert rsp.ok
        assert rsp.status == "Success"
        assert rsp.errors is None
