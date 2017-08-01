import jsonschema

from .exceptions import BadArguments, SchemaError


class Provider(object):
    base_url = None
    provider_name = None
    schema = {}

    def __repr__(self):
        return f'<Notifier:[{self.provider_name.capitalize()}]>'

    @property
    def arguments(self) -> list:
        return dict(self.schema['properties'].items())

    @property
    def required(self) -> list:
        return self.schema.get('required', [])

    def _prepare_data(self, data: dict) -> dict:
        raise NotImplementedError

    def _send_notification(self, data: dict):
        raise NotImplementedError

    def _validate_data(self, data: dict):
        try:
            validator = jsonschema.Draft4Validator()
            validator.check_schema(data)
            validator.validate(data)
        except jsonschema.SchemaError as e:
            raise SchemaError(e.message)
        except jsonschema.ValidationError as e:
            raise BadArguments(e.message)

    def notify(self, **kwargs: dict):
        self._validate_data(kwargs)
        data = self._prepare_data(kwargs)
        return self._send_notification(data)
