def one_or_more(schema: dict, unique_items: bool = True) -> dict:
    """
    Helper function to construct a schema that validates items matching `schema` or an array
     containing items matching `schema`.

    :param schema: The schema to use
    :param unique_items: Flag if array items should be unique
    """
    return {
        'oneOf': [
            {
                'type': 'array',
                'items': schema,
                'minItems': 1,
                'uniqueItems': unique_items
            },
            schema
        ]
    }


def list_to_commas(list_: list) -> str:
    """
    Converts a list of items to a coma separated list. If `list_` is not a list, just return it back

    :param list_: List of items
    :return: A string representing a coma separated list.
    """
    if isinstance(list_, list):
        return ",".join(list_)
    return list_
