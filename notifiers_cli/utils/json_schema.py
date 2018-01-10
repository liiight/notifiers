import click

SCHEMA_BASE_MAP = {
    'string': click.STRING,
    'integer': click.INT,
    'number': click.FLOAT,
    'boolean': click.BOOL
}
COMPLEX_TYPES = ['object', 'array']


def handle_oneof(oneof_schema):
    oneof_dict = {schema['type']: schema for schema in oneof_schema}
    click_type = None
    multiple = False
    description = None
    for key, value in oneof_dict.items():
        if key == 'array':
            continue
        elif key in SCHEMA_BASE_MAP:
            if oneof_dict.get('array') and oneof_dict['array']['items']['type'] == key:
                multiple = True
            # Found a match to a primitive type
            click_type = SCHEMA_BASE_MAP[key]
            description = value.get('title')
            break
    return click_type, multiple, description


def json_schema_to_click_type(schema):
    choices = None
    if isinstance(schema['type'], list):
        if 'string' in schema['type']:
            schema['type'] = 'string'
    click_type = SCHEMA_BASE_MAP[schema['type']]
    description = schema.get('title')
    if schema.get('enum'):
        choices = click.Choice(schema['enum'])
    return click_type, description, choices