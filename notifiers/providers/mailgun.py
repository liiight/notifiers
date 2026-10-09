from __future__ import annotations

import json
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError

from ..core import Provider, Response
from ..models import AsciiStr, Email, FilePath, OneOrMore, RFC2822Datetime, SchemaModel, one_or_more
from ..utils import requests

_EMAIL_LIST_DESCRIPTION = 'Email address of the recipient(s). Example: "Bob <bob@host.com>".'


class MailGunSchema(SchemaModel):
    base_url: Literal["https://api.mailgun.net", "https://api.eu.mailgun.net"] = Field(
        "https://api.mailgun.net", description="MailGun's API base URL. Use https://api.eu.mailgun.net for the EU region"
    )
    api_key: str = Field(description="User's API key")
    message: str | None = Field(None, description="Body of the message. (text version)")
    html: str | None = Field(None, description="Body of the message. (HTML version)")
    to: OneOrMore[str] = Field(description=_EMAIL_LIST_DESCRIPTION)
    from_: Email | None = Field(None, alias="from", description="Email address for From header")
    domain: str = Field(description="MailGun's domain to use")
    cc: OneOrMore[str] | None = Field(None, description=_EMAIL_LIST_DESCRIPTION)
    bcc: OneOrMore[str] | None = Field(None, description=_EMAIL_LIST_DESCRIPTION)
    subject: str | None = Field(None, description="Message subject")
    attachment: OneOrMore[FilePath] | None = Field(None, description="File attachment")
    inline: OneOrMore[FilePath] | None = Field(None, description="Attachment with inline disposition. Can be used to send inline images")
    tag: one_or_more(Annotated[AsciiStr, Field(max_length=128)], max_items=3) | None = Field(None, description="Tag string")
    dkim: bool | None = Field(None, description="Enables/disables DKIM signatures on per-message basis")
    deliverytime: RFC2822Datetime | None = Field(None, description="Desired time of delivery. Note: Messages can be scheduled for a maximum of 3 days in the future.")
    testmode: bool | None = Field(None, description="Enables sending in test mode.")
    tracking: bool | None = Field(None, description="Toggles tracking on a per-message basis")
    tracking_clicks: Literal[True, False, "htmlonly"] | None = Field(
        None,
        description="Toggles clicks tracking on a per-message basis. Has higher priority than domain-level setting. Pass yes, no or htmlonly.",
    )
    tracking_opens: bool | None = Field(None, description="Toggles opens tracking on a per-message basis. Has higher priority than domain-level setting")
    require_tls: bool | None = Field(
        None,
        description="If set to True this requires the message only be sent over a TLS connection."
        " If a TLS connection can not be established, Mailgun will not deliver the message."
        "If set to False, Mailgun will still try and upgrade the connection, but if Mailgun can not,"
        " the message will be delivered over a plaintext SMTP connection.",
    )
    skip_verification: bool | None = Field(
        None,
        description="If set to True, the certificate and hostname will not be verified when trying to establish "
        "a TLS connection and Mailgun will accept any certificate during delivery. If set to False,"
        " Mailgun will verify the certificate and hostname. If either one can not be verified, "
        "a TLS connection will not be established.",
    )
    headers: dict[str, str] | None = Field(None, description="Any other header to add")
    data: dict[str, dict[str, Any]] | None = Field(None, description="attach a custom JSON data to the message")

    @model_validator(mode="after")
    def _check_required(self):
        if not self.is_set("from_"):
            raise PydanticCustomError("required_argument", "'from' is a required property")
        if not (self.is_set("message") or self.is_set("html")):
            raise PydanticCustomError("required_argument", 'Need either "message" or "html"')
        return self


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

    schema_model = MailGunSchema

    def _prepare_data(self, data: dict) -> dict:
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
