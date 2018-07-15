import pytest
from jsonschema import validate, ValidationError

from notifiers.utils.json_schema import format_checker


class TestFormats:
    @pytest.mark.parametrize('formatter, value', [
        ('iso8601', '2018-07-15T07:39:59+00:00'),
        ('iso8601', '2018-07-15T07:39:59Z'),
        ('iso8601', '20180715T073959Z'),
        ('rfc2822', 'Thu, 25 Dec 1975 14:15:16 -0500'),
        ('ascii', 'foo'),
        ('port', '44444'),
        ('port', 44_444),
        ('timestamp', 1531644024),
        ('timestamp', '1531644024'),
        ('e164', '+14155552671'),
        ('e164', '+442071838750'),
        ('e164', '+551155256325')
    ])
    def test_format_positive(self, formatter, value):
        validate(value, {'format': formatter}, format_checker=format_checker)

    def test_valid_file_format(self, tmpdir):
        file_1 = tmpdir.mkdir('foo').join('file_1')
        file_1.write('bar')

        validate(str(file_1), {'format': 'valid_file'}, format_checker=format_checker)

    @pytest.mark.parametrize('formatter, value', [
        ('iso8601', '2018-14-15T07:39:59+00:00'),
        ('iso8601', '2018-07-15T07:39:59Z~'),
        ('iso8601', '20180715T0739545639Z'),
        ('rfc2822', 'Thu 25 Dec14:15:16 -0500'),
        ('ascii', 'פו'),
        ('port', '70000'),
        ('port', 70_000),
        ('timestamp', '15565-5631644024'),
        ('timestamp', '155655631644024'),
        ('e164', '-14155552671'),
        ('e164', '+44207183875063673465'),
        ('e164', '+551155256325zdfgsd')
    ])
    def test_format_negative(self, formatter, value):
        with pytest.raises(ValidationError):
            validate(value, {'format': formatter}, format_checker=format_checker)
