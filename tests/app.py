import typing as tp

from fastapi import Body, FastAPI

from pydantic_json_patch import JsonPatch

app = FastAPI()


@app.patch("/test")
def _(operations: tp.Annotated[JsonPatch, Body()]) -> JsonPatch:
    return operations
