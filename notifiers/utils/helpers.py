from distutils.util import strtobool
import logging
import requests


def text_to_bool(value: str) -> bool:
    """
    Tries to convert a text value to a bool. If unsuccessful returns if value is None or not

    :param value: Value to check
    """
    try:
        return bool(strtobool(value))
    except (ValueError, AttributeError):
        return value is not None


class RequestsHelper:
    """A wrapper around :class:`requests.Session` which enables generically handling HTTP requests"""

    @classmethod
    def request(self, url: str, method: str, logger: logging.Logger, raise_for_status: bool = True,
                path_to_errors: tuple = None, *args,
                **kwargs) -> tuple:
        """
        A wrapper method for :meth:`~requests.Session.request``, which adds some defaults and logging

        :param url: The URL to send the reply to
        :param method: The method to use
        :param raise_for_status: Should an exception be raised for a failed response. Default is **True**
        :param args: Additional args to be sent to the request
        :param kwargs: Additional args to be sent to the request
        :return: Dict of response body or original :class:`requests.Response <Response>`
        """
        session = kwargs.get('session', requests.Session())
        logger.debug('sending a %s request to %s with args: %s kwargs: %s', method.upper(), url, args, kwargs)
        rsp = session.request(method, url, *args, **kwargs)

        logger.debug('response: %s', rsp.text)
        errors = None
        if raise_for_status:
            try:
                rsp.raise_for_status()
            except requests.RequestException as e:
                if e.response is not None:
                    rsp = e.response
                    errors = rsp.json()
                    for arg in path_to_errors:
                        if errors.get(arg):
                            errors = errors[arg]
                    if not isinstance(errors, list):
                        errors = [errors]
                else:
                    rsp = None
                    errors = [str(e)]
                logger.debug('errors when trying to access %s: %s', url, errors)
        return rsp, errors


def get(url: str, *args, **kwargs) -> tuple:
    """Send a GET request. Returns a dict or :class:`requests.Response <Response>`"""
    return RequestsHelper.request(url, 'get', *args, **kwargs)


def post(url: str, *args, **kwargs) -> tuple:
    """Send a POST request. Returns a dict or :class:`requests.Response <Response>`"""
    return RequestsHelper.request(url, 'post', *args, **kwargs)


def delete(url: str, *args, **kwargs) -> tuple:
    """Send a DELETE request. Returns a dict or :class:`requests.Response <Response>`"""
    return RequestsHelper.request(url, 'delete', *args, **kwargs)


def put(url: str, *args, **kwargs) -> tuple:
    """Send a PUT request. Returns a dict or :class:`requests.Response <Response>`"""
    return RequestsHelper.request(url, 'put', *args, **kwargs)


def head(url: str, *args, **kwargs) -> tuple:
    """Send a HEAD request. Returns a dict or :class:`requests.Response <Response>`"""
    return RequestsHelper.request(url, 'head', *args, **kwargs)


def options(url: str, *args, **kwargs) -> tuple:
    """Send a OPTIONS request. Returns a dict or :class:`requests.Response <Response>`"""
    return RequestsHelper.request(url, 'options', *args, **kwargs)
