import re
import typing as tp
from collections.abc import Sequence
from functools import cached_property

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
        pointer = path if isinstance(path, str) else cls._dump_pointer(path)
        return cls(op=op, path=pointer, **kwargs)

    op: tp.Literal["add", "copy", "move", "remove", "replace", "test"]
    """The operation being represented."""

    path: str = Field(examples=["/a/b/c"], pattern=_JSON_POINTER)
    """A JSON pointer representing the path to apply the operation to."""

    @cached_property
    def path_tokens(self) -> tuple[str, ...]:
        """The decoded tokens in the 'path' JSON pointer."""
        return self._load_pointer(self.path)

    @staticmethod
    def _dump_pointer(pointer: Sequence[str]) -> str:
        return "/".join(
            ["", *(token.replace("~", "~0").replace("/", "~1") for token in pointer)]
        )

    @staticmethod
    def _load_pointer(pointer: str) -> tuple[str, ...]:
        return tuple(
            token.replace("~1", "/").replace("~0", "~")
            for token in pointer.split("/")[1:]
        )


class _FromOp(_BaseOp):
    @classmethod
    def create(
        cls, *, path: str | Sequence[str], from_: str | Sequence[str]
    ) -> tx.Self:  # type: ignore[invalid-method-override]
        pointer = from_ if isinstance(from_, str) else cls._dump_pointer(from_)
        return super().create(path=path, **{"from": pointer})

    from_: str = Field(alias="from", examples=["/a/b/d"], pattern=_JSON_POINTER)
    """A JSON pointer representing the path to apply the operation from."""

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
    def from_tokens(self) -> tuple[str, ...]:
        """The decoded tokens in the 'from' JSON pointer."""
        return self._load_pointer(self.from_)


class _ValueOp(_BaseOp):
    @classmethod
    def create(cls, *, path: str | Sequence[str], value: tp.Any) -> tx.Self:  # type: ignore[invalid-method-override]
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
    def create(cls, *, path: str | Sequence[str]) -> tx.Self:  # type: ignore[invalid-method-override]
        return super().create(path=path)

    op: tp.Literal["remove"]


class ReplaceOp(_ValueOp):
    op: tp.Literal["replace"]


class TestOp(_ValueOp):
    op: tp.Literal["test"]


# endregion
