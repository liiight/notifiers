from __future__ import annotations

import json
import logging

import requests

log = logging.getLogger("notifiers")


class RequestsHelper:
    """A wrapper around :class:`requests.Session` which enables generically handling HTTP requests"""

    @classmethod
    def request(
        self,
        url: str,
        method: str,
        raise_for_status: bool = True,
        path_to_errors: tuple | None = None,
        *args,
        **kwargs,
    ) -> tuple:
        """
        A wrapper method for :meth:`~requests.Session.request``, which adds some defaults and logging

        :param url: The URL to send the reply to
        :param method: The method to use
        :param raise_for_status: Should an exception be raised for a failed response. Default is **True**
        :param args: Additional args to be sent to the request
        :param kwargs: Additional args to be sent to the request
        :return: Dict of response body or original :class:`requests.Response`
        """
        session = kwargs.get("session", requests.Session())
        if "timeout" not in kwargs:
            kwargs["timeout"] = (5, 20)
        log.debug(
            "sending a %s request to %s with args: %s kwargs: %s",
            method.upper(),
            url,
            args,
            kwargs,
        )

        if raise_for_status:
            try:
                rsp = session.request(method, url, *args, **kwargs)
                log.debug("response: %s", rsp.text)
                errors = None
                rsp.raise_for_status()
            except requests.RequestException as e:
                if e.response is not None:
                    rsp = e.response
                    if path_to_errors:
                        try:
                            errors = rsp.json()
                            for arg in path_to_errors:
                                if errors.get(arg):
                                    errors = errors[arg]
                        except json.decoder.JSONDecodeError:
                            errors = [rsp.text]
                    else:
                        errors = [rsp.text]
                    if not isinstance(errors, list):
                        errors = [errors]
                else:
                    rsp = None
                    errors = [str(e)]
                log.debug("errors when trying to access %s: %s", url, errors)
        log.debug("returning response %s, errors %s", rsp, errors)
        return rsp, errors


def get(url: str, *args, **kwargs) -> tuple:
    """Send a GET request. Returns a dict or :class:`requests.Response <Response>`"""
    return RequestsHelper.request(url, "get", *args, **kwargs)


def post(url: str, *args, **kwargs) -> tuple:
    """Send a POST request. Returns a dict or :class:`requests.Response <Response>`"""
    return RequestsHelper.request(url, "post", *args, **kwargs)


def file_list_for_request(list_of_paths: list, key_name: str, mimetype: str | None = None) -> list:
    """
    Convenience function to construct a list of files for multiple files upload by :mod:`requests`

    :param list_of_paths: Lists of strings to include in files. Should be pre validated for correctness
    :param key_name: The key name to use for the file list in the request
    :param mimetype: If specified, will be included in the requests
    :return: List of open files ready to be used in a request
    """
    if mimetype:
        return [(key_name, (file, open(file, mode="rb"), mimetype)) for file in list_of_paths]
    return [(key_name, (file, open(file, mode="rb"))) for file in list_of_paths]


try:
    import httpx
except ImportError:
    httpx = None


class AsyncRequestsHelper:
    """A wrapper around :class:`httpx.AsyncClient` which enables generically handling async HTTP requests"""

    @classmethod
    async def request(
        cls,
        url: str,
        method: str,
        raise_for_status: bool = True,
        path_to_errors: tuple | None = None,
        *args,
        **kwargs,
    ) -> tuple:
        """
        A wrapper method for :meth:`httpx.AsyncClient.request`, which adds some defaults and logging

        :param url: The URL to send the reply to
        :param method: The method to use
        :param raise_for_status: Should an exception be raised for a failed response. Default is **True**
        :param path_to_errors: Path to extract error message from response json
        :param args: Additional args to be sent to the request
        :param kwargs: Additional kwargs to be sent to the request
        :return: A tuple of (response, errors)
        """
        if httpx is None:
            raise RuntimeError("The 'httpx' library is required for asynchronous requests. Install it via `pip install httpx` or `pip install notifiers[async]`.")

        if "timeout" not in kwargs:
            kwargs["timeout"] = httpx.Timeout(5.0, read=20.0)
        elif isinstance(kwargs["timeout"], tuple) and len(kwargs["timeout"]) == 2:
            kwargs["timeout"] = httpx.Timeout(kwargs["timeout"][0], read=kwargs["timeout"][1])

        client = kwargs.pop("client", None)
        close_client = False
        if client is None:
            client = httpx.AsyncClient()
            close_client = True

        log.debug(
            "sending an async %s request to %s with args: %s kwargs: %s",
            method.upper(),
            url,
            args,
            kwargs,
        )

        rsp = None
        errors = None
        try:
            rsp = await client.request(method, url, *args, **kwargs)
            log.debug("response: %s", rsp.text)
            if raise_for_status:
                rsp.raise_for_status()
        except httpx.HTTPStatusError as e:
            rsp = e.response
            if path_to_errors:
                try:
                    errors = rsp.json()
                    for arg in path_to_errors:
                        if isinstance(errors, dict) and errors.get(arg):
                            errors = errors[arg]
                except (json.decoder.JSONDecodeError, ValueError):
                    errors = [rsp.text]
            else:
                errors = [rsp.text]
            if not isinstance(errors, list):
                errors = [errors]
            log.debug("errors when trying to access %s: %s", url, errors)
        except httpx.RequestError as e:
            rsp = None
            errors = [str(e)]
            log.debug("errors when trying to access %s: %s", url, errors)
        finally:
            if close_client:
                await client.aclose()

        log.debug("returning response %s, errors %s", rsp, errors)
        return rsp, errors


async def async_get(url: str, *args, **kwargs) -> tuple:
    """Send an async GET request. Returns a tuple of (response, errors)"""
    return await AsyncRequestsHelper.request(url, "get", *args, **kwargs)


async def async_post(url: str, *args, **kwargs) -> tuple:
    """Send an async POST request. Returns a tuple of (response, errors)"""
    return await AsyncRequestsHelper.request(url, "post", *args, **kwargs)
