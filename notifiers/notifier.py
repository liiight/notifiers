from notifiers.exceptions import BadArguments
import jsonschema


class Notifier(object):
    base_url = None
    method = 'post'

    @property
    def schema(self) -> dict:
        raise NotImplementedError

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

    def notify(self, data: dict):
        self._validate_data(data)
        data = self._prepare_data(data)
        rsp = self._send_notification(data)
