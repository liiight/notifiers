import logging

log = logging.getLogger('test_logger')


class TestLogger:
    def test_with_error(self, mock_provider, handler, capsys):
        hdlr = handler(mock_provider.name, logging.INFO)
        log.addHandler(hdlr)

        log.info('test')
        assert '--- Logging error ---' in capsys.readouterr().err

    def test_valid_logging(self, magic_mock_provider, handler):
        hdlr = handler(magic_mock_provider.name, logging.INFO)
        log.addHandler(hdlr)

        log.info('test')
        assert magic_mock_provider.notify.called

    def test_lower_level_log(self, magic_mock_provider, handler):
        hdlr = handler(magic_mock_provider.name, logging.INFO)
        log.addHandler(hdlr)

        log.debug('test')
        assert not magic_mock_provider.notify.called

    def test_with_data(self, magic_mock_provider, handler):
        data = {
            'foo': 'bar'
        }
        hdlr = handler(magic_mock_provider.name, logging.INFO, data)
        log.addHandler(hdlr)

        log.info('test')
        assert magic_mock_provider.notify.called_with(data)

    def test_with_fallback(self, mock_provider, magic_mock_provider, handler):
        hdlr = handler(mock_provider.name, logging.INFO, fallback='magic_mock')
        log.addHandler(hdlr)
        log.info('test')

        assert magic_mock_provider.notify.called

    def test_with_fallback_with_defaults(self, mock_provider, magic_mock_provider, handler):
        fallback_defaults = {
            'foo': 'bar'
        }
        hdlr = handler(mock_provider.name, logging.INFO, fallback='magic_mock', fallback_defaults=fallback_defaults)
        log.addHandler(hdlr)
        log.info('test')

        assert magic_mock_provider.notify.called_with(fallback_defaults)
