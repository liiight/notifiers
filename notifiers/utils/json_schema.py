import re

import jsonschema
import pendulum

# Taken from https://gist.github.com/codehack/6350492822e52b7fa7fe
ISO8601 = re.compile(
    r'^(?P<full>('
    r'(?P<year>\d{4})([/-]?'
    r'(?P<mon>(0[1-9])|(1[012]))([/-]?'
    r'(?P<mday>(0[1-9])|([12]\d)|(3[01])))?)?(?:T'
    r'(?P<hour>([01][0-9])|(?:2[0123]))(:?'
    r'(?P<min>[0-5][0-9])(:?'
    r'(?P<sec>[0-5][0-9]([,.]\d{1,10})?))?)?'
    r'(?:Z|([\-+](?:([01][0-9])|(?:2[0123]))(:?(?:[0-5][0-9]))?))?)?))$'
)


def one_or_more(schema: dict, unique_items: bool = True, min: int = 1, max: int = None) -> dict:
    """
    Helper function to construct a schema that validates items matching
    `schema` or an array containing items matching `schema`.

    :param schema: The schema to use
    :param unique_items: Flag if array items should be unique
    :param min: Correlates to ``minLength`` attribute of JSON Schema array
    :param max: Correlates to ``maxLength`` attribute of JSON Schema array
    """
    multi_schema = {
        'type': 'array',
        'items': schema,
        'minItems': min,
        'uniqueItems': unique_items
    }
    if max:
        multi_schema['maxItems'] = max
    return {
        'oneOf': [
            multi_schema,
            schema
        ]
    }


def list_to_commas(list_of_args) -> str:
    """
    Converts a list of items to a comma separated list. If ``list_of_args`` is
    not a list, just return it back

    :param list_of_args: List of items
    :return: A string representing a comma separated list.
    """
    if isinstance(list_of_args, list):
        return ",".join(list_of_args)
    return list_of_args


format_checker = jsonschema.FormatChecker()


@format_checker.checks('iso8601', raises=ValueError)
def is_iso8601(instance: str):
    if not isinstance(instance, str):
        return True
    return ISO8601.match(instance) is not None


@format_checker.checks('rfc2822', raises=ValueError)
def is_iso8601(instance: str):
    if not isinstance(instance, str):
        return True
    return pendulum.parse(instance).to_rfc2822_string() == instance


@format_checker.checks('ascii', raises=ValueError)
def is_ascii(instance: str):
    if not isinstance(instance, str):
        return True
    return instance.encode('ascii')
