import pytest

from notifiers.exceptions import BadArguments

provider = "msteams"
connector_message_example = {
    "message": "Example of advanced Teams Card, "
    "source: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/"
    "connectors-using?tabs=cURL",
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "themeColor": "0076D7",
    "summary": "Larry Bryant created a new task",
    "sections": [
        {
            "activityTitle": "Larry Bryant created a new task",
            "activitySubtitle": "On Project Tango",
            "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image5.png",
            "facts": [
                {"name": "Assigned to", "value": "Unassigned"},
                {
                    "name": "Due date",
                    "value": "Mon May 01 2017 17:07:18 GMT-0700 (Pacific Daylight Time)",
                },
                {"name": "Status", "value": "Not started"},
            ],
            "markdown": True,
        }
    ],
    "potentialAction": [
        {
            "@type": "ActionCard",
            "name": "Add a comment",
            "inputs": [
                {
                    "@type": "TextInput",
                    "id": "comment",
                    "isMultiline": False,
                    "title": "Add a comment here for this task",
                }
            ],
            "actions": [
                {
                    "@type": "HttpPOST",
                    "name": "Add comment",
                    "target": "https://learn.microsoft.com/outlook/actionable-messages",
                }
            ],
        },
        {
            "@type": "ActionCard",
            "name": "Set due date",
            "inputs": [
                {
                    "@type": "DateInput",
                    "id": "dueDate",
                    "title": "Enter a due date for this task",
                }
            ],
            "actions": [
                {
                    "@type": "HttpPOST",
                    "name": "Save",
                    "target": "https://learn.microsoft.com/outlook/actionable-messages",
                }
            ],
        },
        {
            "@type": "OpenUri",
            "name": "Learn More",
            "targets": [
                {
                    "os": "default",
                    "uri": "https://learn.microsoft.com/outlook/actionable-messages",
                }
            ],
        },
        {
            "@type": "ActionCard",
            "name": "Change status",
            "inputs": [
                {
                    "@type": "MultichoiceInput",
                    "id": "list",
                    "title": "Select a status",
                    "isMultiSelect": "false",
                    "choices": [
                        {"display": "In Progress", "value": "1"},
                        {"display": "Active", "value": "2"},
                        {"display": "Closed", "value": "3"},
                    ],
                }
            ],
            "actions": [
                {
                    "@type": "HttpPOST",
                    "name": "Save",
                    "target": "https://learn.microsoft.com/outlook/actionable-messages",
                }
            ],
        },
    ],
}


class TestMSTeams:
    """MS Teams tests"""

    @pytest.mark.parametrize(
        "data, missing",
        [
            ({"title": "foo", "webhook_url": "bar"}, "message"),
            ({"message": "foo"}, "webhook_url"),
        ],
    )
    def test_msteams_missing_required(self, data, missing, provider):
        data["end_prefix"] = "test"
        with pytest.raises(BadArguments) as e:
            provider.notify(**data)
        assert f"'{missing}' is a required property" in e.value.message

    @pytest.mark.online
    def test_msteams_card(self, provider):
        provider.notify(**connector_message_example)

    @pytest.mark.online
    def test_msteams_simple(self, provider):
        data = {"message": "Foo", "title": "Bar"}
        provider.notify(**data)
