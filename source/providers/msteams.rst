MSTeams
-------
Send notification wiab MS Teams Webhook.
Basic usage is with parameters ``message`` and optional ``title``.
For more advanced usage, additional parameters are allowed. See examples below:

.. code-block:: python

    >>> from notifiers import get_notifier
    >>> teams = get_notifier("msteams")
    >>> # 1) basic usage
    >>> data = {"message": "Foo", "title": "Bar", "webhook_url": "YOUR_WEBHOOK"}
    >>> teams.notify(**data)
    >>> # 2) more complex message
    >>> advanced_message = {
            "webhook_url": "YOUR_WEBHOOK",
            "message": "Example of advanced Teams Card, "
                       "source: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using?tabs=cURL",
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Larry Bryant created a new task",
            "sections": [{
                "activityTitle": "Larry Bryant created a new task",
                "activitySubtitle": "On Project Tango",
                "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image5.png",
                "facts": [{
                    "name": "Assigned to",
                    "value": "Unassigned"
                }, {
                    "name": "Due date",
                    "value": "Mon May 01 2017 17:07:18 GMT-0700 (Pacific Daylight Time)"
                }, {
                    "name": "Status",
                    "value": "Not started"
                }],
                "markdown": True
            }],
            "potentialAction": [{
                "@type": "ActionCard",
                "name": "Add a comment",
                "inputs": [{
                    "@type": "TextInput",
                    "id": "comment",
                    "isMultiline": False,
                    "title": "Add a comment here for this task"
                }],
                "actions": [{
                    "@type": "HttpPOST",
                    "name": "Add comment",
                    "target": "https://learn.microsoft.com/outlook/actionable-messages"
                }]
            }, {
                "@type": "ActionCard",
                "name": "Set due date",
                "inputs": [{
                    "@type": "DateInput",
                    "id": "dueDate",
                    "title": "Enter a due date for this task"
                }],
                "actions": [{
                    "@type": "HttpPOST",
                    "name": "Save",
                    "target": "https://learn.microsoft.com/outlook/actionable-messages"
                }]
            }, {
                "@type": "OpenUri",
                "name": "Learn More",
                "targets": [{
                    "os": "default",
                    "uri": "https://learn.microsoft.com/outlook/actionable-messages"
                }]
            }, {
                "@type": "ActionCard",
                "name": "Change status",
                "inputs": [{
                    "@type": "MultichoiceInput",
                    "id": "list",
                    "title": "Select a status",
                    "isMultiSelect": "false",
                    "choices": [{
                        "display": "In Progress",
                        "value": "1"
                    }, {
                        "display": "Active",
                        "value": "2"
                    }, {
                        "display": "Closed",
                        "value": "3"
                    }]
                }],
                "actions": [{
                    "@type": "HttpPOST",
                    "name": "Save",
                    "target": "https://learn.microsoft.com/outlook/actionable-messages"
                }]
            }]
        }
    >>> teams.notify(**advanced_message)

