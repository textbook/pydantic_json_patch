import re
import typing as tp

from pydantic import BaseModel, ConfigDict, Field

_JSON_POINTER = re.compile(r"^(/[^/]+)*$")

T = tp.TypeVar("T")


class _BaseOp(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    op: tp.Literal["add", "remove"]
    path: str = Field(pattern=_JSON_POINTER)


class AddOp(_BaseOp, tp.Generic[T]):
    op: tp.Literal["add"]
    value: T


class RemoveOp(_BaseOp):
    op: tp.Literal["remove"]
