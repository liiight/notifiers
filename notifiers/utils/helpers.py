import requests

from ..core import Response


def create_response(provider_name: str, data: dict, response: requests.Response = None, failed: bool = False,
                    errors: list = None) -> Response:
    """
    Helper function to generate a :class:`Response` object

    :param provider_name: Name of the provider creating the response
    :param data: The data that was used to send the notification
    :param response: :class:`requests.Response` if exist
    :param failed: Flag to determine if response succeeded or not
    :param errors: List of errors if relevant
    :return: A :class:`Response` object
    """
    status = 'Failure' if failed else 'Success'
    return Response(status=status, provider=provider_name, data=data, response=response, errors=errors)
