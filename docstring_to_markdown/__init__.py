from importlib.metadata import entry_points
from typing import List

from .types import Converter

__version__ = "0.15"


class UnknownFormatError(Exception):
    pass


def _entry_points_sort_key(entry_point):
    if entry_point.dist is None:
        return 0
    if entry_point.dist.name == "docstring_to_markdown":
        return 1
    return 0


def _load_converters() -> List[Converter]:
    converter_entry_points = entry_points().select(
        group="docstring_to_markdown"
    )
    # sort so that the default ones can be overridden
    sorted_entry_points = sorted(
        converter_entry_points,
        key=_entry_points_sort_key
    )
    # de-duplicate
    unique_entry_points = {}
    for entry_point in sorted_entry_points:
        unique_entry_points[entry_point.name] = entry_point

    converters = []
    for entry_point in unique_entry_points.values():
        converter_class = entry_point.load()
        converters.append(converter_class())

    converters.sort(key=lambda converter: -converter.priority)

    return converters


_CONVERTERS = _load_converters()


def convert(docstring: str) -> str:
    for converter in _CONVERTERS:
        if converter.can_convert(docstring):
            return converter.convert(docstring)

    raise UnknownFormatError()
