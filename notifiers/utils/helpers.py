import logging
import os
from distutils.util import strtobool

log = logging.getLogger('notifiers')


def text_to_bool(value: str) -> bool:
    """
    Tries to convert a text value to a bool. If unsuccessful returns if value is None or not

    :param value: Value to check
    """
    try:
        return bool(strtobool(value))
    except (ValueError, AttributeError):
        return value is not None


def merge_dicts(target_dict: dict, merge_dict: dict) -> dict:
    """
    Merges ``merge_dict`` into ``target_dict`` if the latter does not already contain a value for each of the key
    names in ``merge_dict``. Used to cleanly merge default and environ data into notification payload.

    :param target_dict: The target dict to merge into and return, the user provided data for example
    :param merge_dict: The data that should be merged into the target data
    :return: A dict of merged data
    """
    log.debug('merging dict %s into %s', merge_dict, target_dict)
    for key, value in merge_dict.items():
        if key not in target_dict:
            target_dict[key] = value
    return target_dict


def dict_from_environs(prefix: str, name: str, args: list) -> dict:
    """
    Return a dict of environment variables correlating to the arguments list, main name and prefix like so:
    [prefix]_[name]_[arg]

    :param prefix: The environ prefix to use
    :param name: Main part
    :param args: List of args to iterate over
    :return: A dict of found environ values
    """
    environs = {}
    log.debug("starting to collect environs using prefix: '%s'", prefix)
    for arg in args:
        environ = f'{prefix}{name}_{arg}'.upper()
        if os.environ.get(environ):
            environs[arg] = os.environ[environ]
    return environs


def snake_to_camel_case(value: str) -> str:
    """
    Convert a snake case param to CamelCase

    :param value: The value to convert
    :return: A CamelCase value
    """
    log.debug('trying to convert %s to camel case', value)
    return ''.join(word.capitalize() for word in value.split('_'))
