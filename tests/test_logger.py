import logging

import pytest

from notifiers.exceptions import NoSuchNotifierError

log = logging.getLogger("test_logger")


class TestLogger:
    def test_with_error(self, mock_provider, handler, capsys):
        hdlr = handler(mock_provider.name, logging.INFO)
        log.addHandler(hdlr)

        log.info("test")
        assert "--- Logging error ---" in capsys.readouterr().err

    def test_missing_provider(self, handler):
        with pytest.raises(NoSuchNotifierError):
            handler("foo", logging.INFO)

    def test_valid_logging(self, magic_mock_provider, handler):
        hdlr = handler(magic_mock_provider.name, logging.INFO)
        log.addHandler(hdlr)
        assert repr(hdlr) == "<NotificationHandler magic_mock(INFO)>"

        log.info("test")
        magic_mock_provider.notify.assert_called()

    def test_lower_level_log(self, magic_mock_provider, handler):
        hdlr = handler(magic_mock_provider.name, logging.INFO)
        log.addHandler(hdlr)

        log.debug("test")
        magic_mock_provider.notify.assert_not_called()

    def test_with_data(self, magic_mock_provider, handler):
        data = {"foo": "bar"}
        hdlr = handler(magic_mock_provider.name, logging.INFO, data)
        log.addHandler(hdlr)

        log.info("test")
        magic_mock_provider.notify.assert_called_with(foo="bar", message="test", raise_on_errors=True)

    def test_with_fallback(self, magic_mock_provider, handler):
        data = {"env_prefix": "foo"}
        hdlr = handler("pushover", logging.INFO, data, fallback=magic_mock_provider.name)
        log.addHandler(hdlr)
        log.info("test")

        magic_mock_provider.notify.assert_called_with(message="Could not log msg to provider 'pushover'!\nError with sent data: 'user' is a required property")

    def test_with_fallback_with_defaults(self, magic_mock_provider, handler):
        fallback_defaults = {"foo": "bar"}
        data = {"env_prefix": "foo"}
        hdlr = handler(
            "pushover",
            logging.INFO,
            data,
            fallback=magic_mock_provider.name,
            fallback_defaults=fallback_defaults,
        )
        log.addHandler(hdlr)
        log.info("test")

        magic_mock_provider.notify.assert_called_with(
            foo="bar",
            message="Could not log msg to provider 'pushover'!\nError with sent data: 'user' is a required property",
        )
