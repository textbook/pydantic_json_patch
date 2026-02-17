"""Pydantic models for implementing `JSON Patch`_.

.. _JSON Patch: https://datatracker.ietf.org/doc/html/rfc6902/

"""

from importlib.metadata import version

from .models import (
    AddOp,
    CopyOp,
    JsonPatch,
    MoveOp,
    Operation,
    RemoveOp,
    ReplaceOp,
    TestOp,
)

__version__ = version(__name__)

__all__ = [
    "AddOp",
    "CopyOp",
    "JsonPatch",
    "MoveOp",
    "Operation",
    "RemoveOp",
    "ReplaceOp",
    "TestOp",
    "__version__",
]
