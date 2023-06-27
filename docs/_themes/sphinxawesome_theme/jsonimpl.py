"""Custom JSON serializer.

The awesome theme uses custom jinja2 helper functions which are
non-serializable by default. Hence, I need to use a custom JSON
serializer.

:copyright: Copyright Kai Welke.
:license: MIT, see LICENSE for details.
"""
from __future__ import annotations

import json
from typing import IO, Any


class AwesomeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for everything in the `context`."""

    def default(self: AwesomeJSONEncoder, obj: Any) -> str:
        """Return an empty string for anything that's not serializable by default."""
        return ""


def dump(obj: Any, fp: IO[str], *args: Any, **kwargs: Any) -> None:
    """Dump JSON into file."""
    kwargs["cls"] = AwesomeJSONEncoder
    return json.dump(obj, fp, *args, **kwargs)


def dumps(obj: Any, *args: Any, **kwargs: Any) -> str:
    """Convert object to JSON string."""
    kwargs["cls"] = AwesomeJSONEncoder
    return json.dumps(obj, *args, **kwargs)


def load(*args: Any, **kwargs: Any) -> Any:
    """De-serialize JSON."""
    return json.load(*args, **kwargs)


def loads(*args: Any, **kwargs: Any) -> Any:
    """De-serialize JSON."""
    return json.loads(*args, **kwargs)
