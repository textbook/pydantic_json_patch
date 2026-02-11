import re
import typing as tp
from collections.abc import Sequence
from functools import cached_property, lru_cache

import typing_extensions as tx
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

_JSON_POINTER = re.compile(r"^(?:/(?:[^/~]|~[01])+)*$")


# region base models


class _BaseOp(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        model_title_generator=lambda t: f"JsonPatch{t.__name__}eration",
    )

    @classmethod
    def create(cls, *, path: str | Sequence[str], **kwargs) -> tx.Self:
        (op,) = tp.get_args(cls.model_fields["op"].annotation)
        return cls(op=op, path=cls._dump_pointer(path), **kwargs)

    op: tp.Literal["add", "copy", "move", "remove", "replace", "test"]
    """The operation being represented."""

    path: str = Field(examples=["/a/b/c"], pattern=_JSON_POINTER)
    """A JSON pointer representing the path to apply the operation to."""

    @cached_property
    def path_tokens(self) -> tuple[str, ...]:
        """The decoded tokens in the 'path' JSON pointer."""
        return self._load_pointer(self.path)

    @classmethod
    def _dump_pointer(cls, pointer: Sequence[str]) -> str:
        if isinstance(pointer, str):
            return pointer
        return "/".join(["", *(cls._encode_token(token) for token in pointer)])

    @staticmethod
    @lru_cache
    def _decode_token(token: str) -> str:
        return token.replace("~1", "/").replace("~0", "~")

    @staticmethod
    @lru_cache
    def _encode_token(token: str) -> str:
        return token.replace("~", "~0").replace("/", "~1")

    @classmethod
    @lru_cache
    def _load_pointer(cls, pointer: str) -> tuple[str, ...]:
        return tuple(cls._decode_token(token) for token in pointer.split("/")[1:])


class _FromOp(_BaseOp):
    @classmethod
    def create(
        cls, *, path: str | Sequence[str], from_: str | Sequence[str]
    ) -> tx.Self:  # ty: ignore[invalid-method-override]
        pointer = from_ if isinstance(from_, str) else cls._dump_pointer(from_)
        return super().create(path=path, **{"from": pointer})

    from_: str = Field(alias="from", examples=["/a/b/d"], pattern=_JSON_POINTER)
    """A JSON pointer representing the path to apply the operation from."""

    @model_validator(mode="before")
    @classmethod
    def _pre_validate(cls, data: tp.Any, info: ValidationInfo) -> tp.Any:
        if (
            info.mode != "json"  # pragma: no mutate
            and isinstance(data, dict)
            and "from_" in data
            and "from" not in data
        ):
            data["from"] = data.pop("from_")
        return data

    @cached_property
    def from_tokens(self) -> tuple[str, ...]:
        """The decoded tokens in the 'from' JSON pointer."""
        return self._load_pointer(self.from_)


class _ValueOp(_BaseOp):
    @classmethod
    def create(cls, *, path: str | Sequence[str], value: tp.Any) -> tx.Self:  # ty: ignore[invalid-method-override]
        return super().create(path=path, value=value)

    value: tp.Any = Field(examples=[42])
    """The value to use in the operation."""


# endregion

# region public models


class AddOp(_ValueOp):
    op: tp.Literal["add"]


class CopyOp(_FromOp):
    op: tp.Literal["copy"]


class MoveOp(_FromOp):
    op: tp.Literal["move"]


class RemoveOp(_BaseOp):
    @classmethod
    def create(cls, *, path: str | Sequence[str]) -> tx.Self:  # ty: ignore[invalid-method-override]
        return super().create(path=path)

    op: tp.Literal["remove"]


class ReplaceOp(_ValueOp):
    op: tp.Literal["replace"]


class TestOp(_ValueOp):
    op: tp.Literal["test"]


# endregion
