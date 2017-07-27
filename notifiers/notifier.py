from notifiers.exceptions import MissingRequired


class Notifier(object):
    base_url = None
    method = 'post'

    @property
    def schema(self):
        raise NotImplementedError

    @property
    def arguments(self):
        return self.schema['properties']

    @property
    def required(self):
        return self.arguments.get('required', [])

    def _send_notification(self, **kwargs):
        raise NotImplementedError

    def _validate_required(self, **kwargs):
        return all(req in kwargs for req in self.required)

    def notify(self, **kwargs):
        if not self._validate_required(**kwargs):
            raise MissingRequired(self.required)
        self._send_notification(**kwargs)
