import re
import typing as tp
from functools import cached_property

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core.core_schema import ValidationInfo

_JSON_POINTER = re.compile(r"^(/[^/]+)*$")

T = tp.TypeVar("T")
Tokens: tp.TypeAlias = tuple[str, ...]


class _BaseOp(BaseModel):
    model_config = ConfigDict(frozen=True)

    op: tp.Literal["add", "remove"]
    path: str = Field(examples=["/a/b/c"], pattern=_JSON_POINTER)

    @cached_property
    def path_tokens(self) -> Tokens:
        return self._parse_pointer(self.path)

    @classmethod
    def _parse_pointer(cls, pointer: str) -> Tokens:
        return tuple(
            token.replace("~1", "/").replace("~0", "~")
            for token in pointer.split("/")[1:]
        )


class _ValueOp(_BaseOp, tp.Generic[T]):
    value: T


class AddOp(_ValueOp, tp.Generic[T]):
    op: tp.Literal["add"]


class _FromOp(_BaseOp):
    from_: str = Field(alias="from", examples=["/a/b/d"], pattern=_JSON_POINTER)

    @model_validator(mode="before")
    @classmethod
    def _pre_validate(cls, data: tp.Any, info: ValidationInfo) -> tp.Any:
        if (
            info.mode != "json"
            and isinstance(data, dict)
            and "from_" in data
            and "from" not in data
        ):
            data["from"] = data.pop("from_")
        return data

    @cached_property
    def from_tokens(self) -> Tokens:
        return self._parse_pointer(self.from_)


class CopyOp(_FromOp):
    op: tp.Literal["copy"]


class MoveOp(_FromOp):
    op: tp.Literal["move"]


class RemoveOp(_BaseOp):
    op: tp.Literal["remove"]


class ReplaceOp(_ValueOp, tp.Generic[T]):
    op: tp.Literal["replace"]


class TestOp(_ValueOp, tp.Generic[T]):
    op: tp.Literal["test"]
