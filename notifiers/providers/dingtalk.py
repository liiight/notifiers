from __future__ import annotations

import re
from typing import Literal

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError

from ..core import Provider, Response
from ..models import SchemaModel, Url
from ..utils import requests


class DingTalkText(SchemaModel):
    content: str = Field(min_length=1, max_length=20000, description="Message content")


class DingTalkMarkdown(SchemaModel):
    title: str = Field(min_length=1, max_length=100, description="Message title")
    text: str = Field(min_length=1, max_length=20000, description="Markdown content")


class DingTalkLink(SchemaModel):
    title: str = Field(min_length=1, max_length=100, description="Link title")
    text: str = Field(min_length=1, max_length=500, description="Link description")
    message_url: Url = Field(min_length=1, alias="messageUrl", description="Link URL")
    pic_url: Url = Field("", alias="picUrl", description="Image URL")


class DingTalkActionCard(SchemaModel):
    title: str = Field(min_length=1, max_length=100, description="Card title")
    text: str = Field(min_length=1, max_length=20000, description="Card content")
    single_title: str = Field(min_length=1, max_length=50, alias="singleTitle", description="Button text")
    single_url: Url = Field(min_length=1, alias="singleURL", description="Button URL")
    btn_orientation: Literal["0", "1"] = Field("0", alias="btnOrientation", description="Button layout")


class DingTalkMessage(SchemaModel):
    msg_type: Literal["text", "markdown", "link", "actionCard"] = Field("text", alias="msgtype", description="Message type")
    text: DingTalkText | None = None
    markdown: DingTalkMarkdown | None = None
    link: DingTalkLink | None = None
    action_card: DingTalkActionCard | None = Field(None, alias="actionCard")

    @model_validator(mode="after")
    def _content_matches_type(self):
        content_field = {"actionCard": "action_card"}.get(self.msg_type, self.msg_type)
        if getattr(self, content_field) is None:
            raise PydanticCustomError("missing_content", "'{msgtype}' content is required when 'msgtype' is '{msgtype}'", {"msgtype": self.msg_type})
        return self


MOBILE_RE = re.compile(r"^1[3-9]\d{9}$")


class DingTalkAt(SchemaModel):
    at_mobiles: list[str] | None = Field(None, max_length=20, alias="atMobiles", description="Phone numbers to @")
    at_user_ids: list[str] | None = Field(None, max_length=20, alias="atUserIds", description="User IDs to @")
    is_at_all: bool = Field(False, alias="isAtAll", description="Notify all members")

    @model_validator(mode="after")
    def _check_items(self):
        for mobile in self.at_mobiles or []:
            if not MOBILE_RE.match(mobile):
                raise PydanticCustomError("pattern", "'{value}' is not a valid mobile number", {"value": mobile})
        for user_id in self.at_user_ids or []:
            if not user_id:
                raise PydanticCustomError("min_length", "User IDs must not be empty")
        return self


class DingTalkSchema(SchemaModel):
    access_token: str = Field(min_length=1, description="Webhook access token. Obtain from DingTalk Robot settings")
    msg_data: DingTalkMessage | None = Field(None, description="Full message payload. Use this or 'message'")
    message: str | None = Field(None, min_length=1, max_length=20000, description="Text message content. Shorthand for a 'text' type 'msg_data'")
    at: DingTalkAt | None = None
    sign: str | None = Field(None, min_length=1, description="Secret signature. Required if secret is set in webhook")
    timestamp: str | None = Field(None, pattern=r"^\d{13}$", description="Sign timestamp")

    @model_validator(mode="after")
    def _message_or_msg_data(self):
        passed = [name for name in ("msg_data", "message") if self.is_set(name)]
        if not passed:
            raise PydanticCustomError("required_argument", "One of 'msg_data', 'message' is required")
        if len(passed) > 1:
            raise PydanticCustomError("message_or_msg_data", "Only one of 'msg_data' or 'message' is allowed")
        return self


class DingTalk(Provider):
    """Send DingTalk notifications via Robot Webhook"""

    base_url = "https://oapi.dingtalk.com/robot/send"
    site_url = "https://open.dingtalk.com/document/"
    name = "dingtalk"
    path_to_errors = ("errmsg",)

    schema_model = DingTalkSchema

    def _prepare_data(self, data: dict) -> dict:
        """
        Builds the payload expected by the DingTalk robot API.
        Docs: https://open.dingtalk.com/document/orgapp-server/custom-robot-access
        """
        msg_data = data.pop("msg_data", None) or {"text": {"content": data.pop("message")}}
        # `msgtype` is omitted when the default ("text") is used, since only passed values are kept
        msgtype = msg_data.get("msgtype", "text")
        payload = {"access_token": data["access_token"], "msgtype": msgtype, msgtype: msg_data[msgtype]}

        if "at" in data:
            payload["at"] = data["at"]

        # Signature handling
        if "sign" in data and "timestamp" in data:
            payload["sign"] = data["sign"]
            payload["timestamp"] = data["timestamp"]

        return payload

    def _send_notification(self, data: dict) -> Response:
        params = {"access_token": data.pop("access_token")}
        response, errors = requests.post(self.base_url, params=params, json=data, path_to_errors=self.path_to_errors)
        if not errors and response is not None:
            # DingTalk returns HTTP 200 with a non zero errcode on failure
            body = response.json()
            if body.get("errcode"):
                errors = [body.get("errmsg") or str(body)]
        return self.create_response(data, response, errors)
