import json
from typing import Dict
from typing import Union

from pendulum import DateTime
from pendulum import now
from pydantic import conint
from pydantic import EmailStr
from pydantic import Field
from pydantic import FilePath
from pydantic import Json
from pydantic import NameEmail
from pydantic import root_validator
from pydantic import validator
from typing_extensions import Literal

from ..models.provider import Provider
from ..models.provider import SchemaModel
from ..models.response import Response
from ..utils import requests


class MailGunSchema(SchemaModel):
    api_key: str = Field(..., description="User's API key")
    domain: str = Field(..., description="The domain to use")
    from_: NameEmail = Field(
        ..., description="Email address for 'From' header", alias="from"
    )
    to: SchemaModel.single_or_list(NameEmail) = Field(
        ..., description="Email address of the recipient(s)"
    )
    cc: SchemaModel.single_or_list(NameEmail) = Field(
        None, description="Email address of the CC recipient(s)"
    )
    bcc: SchemaModel.single_or_list(NameEmail) = Field(
        None, description="Email address of the BCC recipient(s)"
    )
    subject: str = Field(None, description="Message subject")
    message: str = Field(
        None, description="Body of the message. (text version)", alias="text"
    )
    html: str = Field(None, description="Body of the message. (HTML version)")
    amp_html: str = Field(
        None,
        description="AMP part of the message. Please follow google guidelines to compose and send AMP emails.",
        alias="amp-html",
    )
    attachment: SchemaModel.single_or_list(FilePath) = Field(
        None, description="File attachment(s)"
    )
    inline: SchemaModel.single_or_list(FilePath) = Field(
        None,
        description="Attachment with inline disposition. Can be used to send inline images",
    )
    template: str = Field(
        None, description="Name of a template stored via template API"
    )
    version: str = Field(
        None,
        description="Use this parameter to send a message to specific version of a template",
        alias="t:version",
    )
    t_text: bool = Field(
        None,
        description="Pass yes if you want to have rendered template in the text part of the message"
        " in case of template sending",
        alias="t:text",
    )
    tag: SchemaModel.single_or_list(str) = Field(
        None,
        description="Tag string. See Tagging for more information",
        alias="o:tag",
        max_items=3,
        max_length=128,
    )
    dkim: bool = Field(
        None,
        description="Enables/disables DKIM signatures on per-message basis. Pass yes, no, true or false",
        alias="o:dkim",
    )
    delivery_time: DateTime = Field(
        None,
        description="Desired time of delivery. Note: Messages can be scheduled for a maximum of 3 days in the future.",
        alias="o:deliverytime",
    )
    delivery_time_optimize_period: conint(gt=23, lt=73) = Field(
        None,
        description="This value defines the time window (in hours) in which Mailgun will run the optimization "
        "algorithm based on prior engagement data of a given recipient",
        alias="o:deliverytime-optimize-period",
    )
    test_mode: bool = Field(
        None, description="Enables sending in test mode", alias="o:testmode"
    )
    tracking: bool = Field(
        None, description="Toggles tracking on a per-message basis", alias="o:tracking"
    )
    tracking_clicks: Union[bool, Literal["htmlonly"]] = Field(
        None,
        description="Toggles clicks tracking on a per-message basis. Has higher priority than domain-level setting",
        alias="o:tracking-clicks",
    )
    tracking_opens: bool = Field(
        None,
        description="Toggles opens tracking on a per-message basis.",
        alias="o:tracking-opens",
    )
    require_tls: bool = Field(
        None,
        description="If set to True or yes this requires the message only be sent over a TLS connection."
        " If a TLS connection can not be established, Mailgun will not deliver the message."
        " If set to False or no, Mailgun will still try and upgrade the connection, "
        "but if Mailgun can not, the message will be delivered over a plaintext SMTP connection",
        alias="o:require-tls",
    )
    skip_verification: bool = Field(
        None,
        description="If set to True or yes, the certificate and hostname will not be verified when trying to establish "
        "a TLS connection and Mailgun will accept any certificate during delivery."
        " If set to False or no, Mailgun will verify the certificate and hostname."
        " If either one can not be verified, a TLS connection will not be established.",
        alias="o:skip-verification",
    )

    headers: SchemaModel.single_or_list(Dict[str, str]) = Field(
        None,
        description="Add arbitrary value(s) to append a custom MIME header to the message",
    )
    data: SchemaModel.single_or_list(Dict[str, Json]) = Field(
        None, description="Attach a custom JSON data to the message"
    )
    recipient_variables: Dict[EmailStr, Dict[str, str]] = Field(
        None,
        description="A valid JSON-encoded dictionary, where key is a plain recipient address and value is a "
        "dictionary with variables that can be referenced in the message body.",
        alias="recipient-variables",
    )

    @validator("tag", pre=True, each_item=True)
    def validate_tag(cls, v):
        if not isinstance(v, list):
            v = [v]
        for v_ in v:
            try:
                v_.encode("ascii")
            except UnicodeEncodeError:
                raise ValueError("Value must be valid ascii")
        return v

    @root_validator()
    def headers_and_data(cls, values):
        def transform(key_name, prefix, json_dump):
            data_to_transform = values.pop(key_name, None)
            if data_to_transform:
                if not isinstance(data_to_transform, list):
                    data_to_transform = [data_to_transform]
                for data_ in data_to_transform:
                    for name, value in data_.items():
                        if json_dump:
                            value = json.dumps(value)
                        values[f"{prefix}:{name}"] = value

        transform("headers", "h", False)
        transform("data", "v", True)
        return values

    @root_validator(pre=True)
    def validate_body(cls, values):
        if not any(value in values for value in ("message", "html")):
            raise ValueError("Either 'text' or 'html' are required")
        return values

    @validator("delivery_time_optimize_period")
    def hours_to_str(cls, v):
        return f"{v}h"

    @validator("delivery_time", pre=True)
    def valid_delivery_time(cls, v: DateTime):
        if v.diff(now("utc")).days > 3:
            raise ValueError(
                "Messages can be scheduled for a maximum of 3 days in the future"
            )
        return v.to_rfc2822_string()

    @validator("t_text", "test_mode")
    def true_to_yes(cls, v):
        return "yes" if v else "no"

    @validator("dkim", "tracking", "tracking_clicks", "tracking_opens")
    def text_bool(cls, v):
        return str(v).lower() if isinstance(v, bool) else v

    @validator("to", "cc", "bcc")
    def comma(cls, v):
        return cls.to_comma_separated(v)


class MailGun(Provider):
    """Send emails via MailGun"""

    base_url = "https://api.mailgun.net/v3/{domain}/messages"
    site_url = "https://documentation.mailgun.com/"
    name = "mailgun"
    path_to_errors = ("message",)

    def _send_notification(self, data: MailGunSchema) -> Response:
        data = data.dict(by_alias=True, exclude_none=True)
        url = self.base_url.format(domain=data.pop("domain"))
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
