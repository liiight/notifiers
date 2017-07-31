import jsonschema

from .exceptions import BadArguments


class Provider(object):
    base_url = None
    schema = {}

    @property
    def arguments(self) -> list:
        return self.schema['properties'].keys()

    @property
    def required(self) -> list:
        return self.schema['properties'].get('required', [])

    def _prepare_data(self, data: dict) -> dict:
        raise NotImplementedError

    def _send_notification(self, data: dict):
        raise NotImplementedError

    def _validate_data(self, data: dict):
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.ValidationError as e:
            raise BadArguments(e.message)

    def notify(self, **kwargs: dict):
        self._validate_data(kwargs)
        data = self._prepare_data(kwargs)
        rsp = self._send_notification(data)
