import typing as tp
from uuid import UUID

from fastapi import Body, FastAPI

from pydantic_json_patch import JsonPatch

app = FastAPI()


@app.patch("/resource/{resource_id}")
def _(resource_id: UUID, operations: tp.Annotated[JsonPatch, Body()]) -> JsonPatch:  # noqa: ARG001
    return operations
