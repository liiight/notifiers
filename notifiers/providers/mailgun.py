import json

from ..core import Provider
from ..core import Response
from ..utils import requests
from ..utils.schema.helpers import one_or_more


class MailGun(Provider):
    """Send emails via MailGun"""

    base_url = "https://api.mailgun.net/v3/{domain}/messages"
    site_url = "https://documentation.mailgun.com/"
    name = "mailgun"
    path_to_errors = ("message",)

    __properties_to_change = [
        "tag",
        "dkim",
        "deliverytime",
        "testmode",
        "tracking",
        "tracking_clicks",
        "tracking_opens",
        "require_tls",
        "skip_verification",
    ]

    __email_list = one_or_more(
        {
            "type": "string",
            "title": 'Email address of the recipient(s). Example: "Bob <bob@host.com>".',
        }
    )

    _required = {
        "allOf": [
            {"required": ["to", "domain", "api_key"]},
            {"anyOf": [{"required": ["from"]}, {"required": ["from_"]}]},
            {
                "anyOf": [{"required": ["message"]}, {"required": ["html"]}],
                "error_anyOf": 'Need either "message" or "html"',
            },
        ]
    }

    defaults = {"base_url": "https://api.mailgun.net"}

    _schema = {
        "type": "object",
        "properties": {
            "base_url": {
                "type": "string",
                "enum": ["https://api.mailgun.net", "https://api.eu.mailgun.net"],
            },
            "api_key": {"type": "string", "title": "User's API key"},
            "message": {
                "type": "string",
                "title": "Body of the message. (text version)",
            },
            "html": {"type": "string", "title": "Body of the message. (HTML version)"},
            "to": __email_list,
            "from": {
                "type": "string",
                "format": "email",
                "title": "Email address for From header",
            },
            "from_": {
                "type": "string",
                "format": "email",
                "title": "Email address for From header",
                "duplicate": True,
            },
            "domain": {"type": "string", "title": "MailGun's domain to use"},
            "cc": __email_list,
            "bcc": __email_list,
            "subject": {"type": "string", "title": "Message subject"},
            "attachment": one_or_more(
                {"type": "string", "format": "valid_file", "title": "File attachment"}
            ),
            "inline": one_or_more(
                {
                    "type": "string",
                    "format": "valid_file",
                    "title": "Attachment with inline disposition. Can be used to send inline images",
                }
            ),
            "tag": one_or_more(
                schema={
                    "type": "string",
                    "format": "ascii",
                    "title": "Tag string",
                    "maxLength": 128,
                },
                max=3,
            ),
            "dkim": {
                "type": "boolean",
                "title": "Enables/disables DKIM signatures on per-message basis",
            },
            "deliverytime": {
                "type": "string",
                "format": "rfc2822",
                "title": "Desired time of delivery. Note: Messages can be scheduled for a maximum of 3 days in "
                "the future.",
            },
            "testmode": {"type": "boolean", "title": "Enables sending in test mode."},
            "tracking": {
                "type": "boolean",
                "title": "Toggles tracking on a per-message basis",
            },
            "tracking_clicks": {
                "type": ["string", "boolean"],
                "title": "Toggles clicks tracking on a per-message basis. Has higher priority than domain-level"
                " setting. Pass yes, no or htmlonly.",
                "enum": [True, False, "htmlonly"],
            },
            "tracking_opens": {
                "type": "boolean",
                "title": "Toggles opens tracking on a per-message basis. Has higher priority than domain-level setting",
            },
            "require_tls": {
                "type": "boolean",
                "title": "If set to True this requires the message only be sent over a TLS connection."
                " If a TLS connection can not be established, Mailgun will not deliver the message."
                "If set to False, Mailgun will still try and upgrade the connection, but if Mailgun can not,"
                " the message will be delivered over a plaintext SMTP connection.",
            },
            "skip_verification": {
                "type": "boolean",
                "title": "If set to True, the certificate and hostname will not be verified when trying to establish "
                "a TLS connection and Mailgun will accept any certificate during delivery. If set to False,"
                " Mailgun will verify the certificate and hostname. If either one can not be verified, "
                "a TLS connection will not be established.",
            },
            "headers": {
                "type": "object",
                "additionalProperties": {"type": "string"},
                "title": "Any other header to add",
            },
            "data": {
                "type": "object",
                "additionalProperties": {"type": "object"},
                "title": "attach a custom JSON data to the message",
            },
        },
        "additionalProperties": False,
    }

    def _prepare_data(self, data: dict) -> dict:
        if data.get("from_"):
            data["from"] = data.pop("from_")

        new_data = {
            "to": data.pop("to"),
            "from": data.pop("from"),
            "domain": data.pop("domain"),
            "api_key": data.pop("api_key"),
        }

        if data.get("message"):
            new_data["text"] = data.pop("message")

        if data.get("attachment"):
            attachment = data.pop("attachment")
            if isinstance(attachment, str):
                attachment = [attachment]
            new_data["attachment"] = attachment

        if data.get("inline"):
            inline = data.pop("inline")
            if isinstance(inline, str):
                inline = [inline]
            new_data["inline"] = inline

        for property_ in self.__properties_to_change:
            if data.get(property_):
                new_property = f"o:{property_}".replace("_", "-")
                new_data[new_property] = data.pop(property_)

        if data.get("headers"):
            for key, value in data["headers"].items():
                new_data[f"h:{key}"] = value
            del data["headers"]

        if data.get("data"):
            for key, value in data["data"].items():
                new_data[f"v:{key}"] = json.dumps(value)
            del data["data"]

        for key, value in data.items():
            new_data[key] = value

        return new_data

    def _send_notification(self, data: dict) -> Response:
        base_url = data.pop("base_url")
        domain = data.pop("domain")
        url = f"{base_url}/v3/{domain}/messages"
        auth = "api", data.pop("api_key")
        files = []
        if data.get("attachment"):
            files += requests.file_list_for_request(data["attachment"], "attachment")
        if data.get("inline"):
            files += requests.file_list_for_request(data["inline"], "inline")

        response, errors = requests.post(
            url=url,
            data=data,
            auth=auth,
            files=files,
            path_to_errors=self.path_to_errors,
        )
        return self.create_response(data, response, errors)
