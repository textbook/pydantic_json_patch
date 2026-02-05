import re
import typing as tp

from pydantic import BaseModel, ConfigDict, Field

_JSON_POINTER = re.compile(r"^(/[^/]+)*$")


class RemoveOp(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    op: tp.Literal["remove"]
    path: str = Field(pattern=_JSON_POINTER)
