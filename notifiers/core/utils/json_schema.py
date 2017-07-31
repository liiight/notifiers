def one_or_more(schema: dict, unique_items: bool = True) -> dict:
    """
    Helper function to construct a schema that validates items matching `schema` or an array
    containing items matching `schema`.
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
