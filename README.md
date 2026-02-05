# Pydantic JSON Patch

[Pydantic] models for implementing [JSON Patch].

## FastAPI

You can use this package to validate a JSON Patch endpoint in a FastAPI application:

```python
import typing as tp

from fastapi import Body, FastAPI

from pydantic_json_patch import JsonPatch

app = FastAPI()


@app.patch("/resource/:id")
def _(operations: tp.Annotated[JsonPatch, Body()]) -> "...":
    ...
```

  [fastapi]: https://fastapi.tiangolo.com/
  [json patch]: https://datatracker.ietf.org/doc/html/rfc6902/
  [pydantic]: https://docs.pydantic.dev/latest/
