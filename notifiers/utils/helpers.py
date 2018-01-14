from distutils.util import strtobool


def text_to_bool(value: str) -> bool:
    """
    Tries to convert a text value to a bool. If unsuccessful returns if value is None or not

    :param value: Value to check
    """
    try:
        return bool(strtobool(value))
    except (ValueError, AttributeError):
        return value is not None
