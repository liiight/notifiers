"""
Sphinx directive that renders a provider's (or resource's) arguments from its pydantic schema model, so the docs can't
drift from the code.

Usage::

    .. provider-arguments:: pushover
    .. provider-arguments:: telegram.updates
"""

from __future__ import annotations

import re
import types
import typing
from typing import Annotated, Literal

from docutils import nodes
from docutils.parsers.rst import Directive
from pydantic import BaseModel

import notifiers
from notifiers.models.base import field_key, field_names

_NONE = type(None)


def _union_name(args) -> str:
    names = list(dict.fromkeys(_type_name(a) for a in args if a is not _NONE))
    # OneOrMore[T] is "list[T] | T"
    if len(names) == 2 and names[0] == f"list[{names[1]}]":
        return f"{names[1]} or list of {names[1]}"
    return " | ".join(names)


_RENDERERS = {
    Annotated: lambda args: _type_name(args[0]),
    Literal: lambda args: " | ".join(repr(a) for a in args),
    typing.Union: _union_name,
    types.UnionType: _union_name,
    list: lambda args: f"list[{_type_name(args[0])}]",
    dict: lambda _: "dict",
}


def _type_name(annotation) -> str:
    """A short, human readable type"""
    renderer = _RENDERERS.get(typing.get_origin(annotation))
    if renderer:
        return renderer(typing.get_args(annotation))
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return "object"
    return getattr(annotation, "__name__", str(annotation))


def _constraints(field) -> str:
    parts = []
    for meta in field.metadata:
        for attr, label in (("ge", "≥"), ("le", "≤"), ("gt", ">"), ("lt", "<"), ("min_length", "min length"), ("max_length", "max length")):
            value = getattr(meta, attr, None)
            if value is not None:
                parts.append(f"{label} {value}")
    return ", ".join(parts)


def _resolve(target: str):
    provider_name, _, resource = target.partition(".")
    provider = notifiers.get_notifier(provider_name, strict=True)
    return getattr(provider, resource) if resource else provider


class ProviderArguments(Directive):
    required_arguments = 1
    has_content = False

    def run(self):
        resource = _resolve(self.arguments[0])
        model = resource.schema_model
        required = set(resource.required["required"])
        defaults = resource.defaults

        table = nodes.table()
        group = nodes.tgroup(cols=4)
        table += group
        for width in (20, 15, 10, 55):
            group += nodes.colspec(colwidth=width)
        head = nodes.thead()
        group += head
        body = nodes.tbody()
        group += body

        def row(cells):
            tr = nodes.row()
            for cell in cells:
                entry = nodes.entry()
                entry += cell if isinstance(cell, nodes.Node) else nodes.paragraph(text=cell)
                tr += entry
            return tr

        head += row(["Argument", "Type", "Required", "Description"])
        for name, field in model.model_fields.items():
            key = field_key(name, field)
            argument = nodes.paragraph()
            argument += nodes.literal(text=key)
            others = [n for n in field_names(name, field) if n != key]
            if others:
                argument += nodes.Text(" (also " + ", ".join(others) + ")")
            description = field.description or ""
            extras = []
            if key in defaults:
                default = defaults[key]
                if key == "from" and isinstance(default, str) and default.startswith("notifiers@"):
                    default = "notifiers@<hostname>"
                extras.append(f"Default: {default!r}")
            constraints = _constraints(field)
            if constraints:
                extras.append(constraints)
            if extras:
                description = f"{description.rstrip('.')}. {'. '.join(extras)}" if description else ". ".join(extras)
            description = re.sub(r"\.\.+", ".", description)
            body += row([argument, _type_name(field.annotation), "yes" if key in required else "", description])
        return [table]


def setup(app):
    app.add_directive("provider-arguments", ProviderArguments)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
