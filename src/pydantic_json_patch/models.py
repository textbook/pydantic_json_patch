import re
import typing as tp

from pydantic import BaseModel, ConfigDict, Field

_JSON_POINTER = re.compile(r"^(/[^/]+)*$")

T = tp.TypeVar("T")


class _BaseOp(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    op: tp.Literal["add", "remove"]
    path: str = Field(pattern=_JSON_POINTER)


class _ValueOp(_BaseOp, tp.Generic[T]):
    value: T


class AddOp(_ValueOp, tp.Generic[T]):
    op: tp.Literal["add"]


class RemoveOp(_BaseOp):
    op: tp.Literal["remove"]


class ReplaceOp(_ValueOp, tp.Generic[T]):
    op: tp.Literal["replace"]


class TestOp(_ValueOp, tp.Generic[T]):
    op: tp.Literal["test"]
