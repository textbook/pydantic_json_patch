# ruff: noqa: ARG001
import typing as tp
from uuid import UUID

from fastapi import Body, FastAPI
from pydantic import Discriminator

from pydantic_json_patch import AddOp, JsonPatch, TestOp

app = FastAPI()


@app.patch("/resource/{resource_id}")
def _(resource_id: UUID, operations: tp.Annotated[JsonPatch, Body()]) -> JsonPatch:
    return operations


@app.patch("/other_resource/{relevant_id}")
def _(
    relevant_id: int,
    operations: tp.Annotated[
        list[tp.Annotated[AddOp[int] | TestOp[int], Discriminator("op")]], Body()
    ],
) -> None:
    return
