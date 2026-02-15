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
    "__version__",
    "AddOp",
    "CopyOp",
    "JsonPatch",
    "MoveOp",
    "Operation",
    "RemoveOp",
    "ReplaceOp",
    "TestOp",
]
