import typing as tp
from importlib.metadata import version

from pydantic import Discriminator

from .models import AddOp, CopyOp, MoveOp, RemoveOp, ReplaceOp, TestOp, Tokens

__version__ = version(__name__)

Operation: tp.TypeAlias = tp.Annotated[
    tp.Union[AddOp, CopyOp, MoveOp, RemoveOp, ReplaceOp, TestOp], Discriminator("op")
]
JsonPatch: tp.TypeAlias = list[Operation]

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
    "Tokens",
]
