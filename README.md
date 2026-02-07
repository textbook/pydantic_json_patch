# Pydantic JSON Patch

[Pydantic] models for implementing [JSON Patch].

## Models

A model is provided for each of the six JSON Patch operations:

- `AddOp`
- `CopyOp`
- `MoveOp`
- `RemoveOp`
- `ReplaceOp`
- `TestOp`

As repeating the op is a bit awkward (`CopyOp(op="copy", ...)`), a `create` factory method is available:

```pycon
>>> from pydantic_json_patch import AddOp
>>> op = AddOp.create(path="/foo/bar", value=123)
>>> op
AddOp(op='add', path='/foo/bar', value=123)
>>> op.model_dump_json()
'{"op":"add","path":"/foo/bar","value":123}'
```

Additionally, there are two compound models:

- `Operation` is the union of all the operators; and
- `JsonPatch` represents a list of that union type.

### Pointer tokens

The `path` property (and `from` property, where present) of an operation is a [JSON Pointer].
This means that any `~` or `/` characters in property names need to be properly encoded.
To aid working with these, the models expose a read-only `path_tokens` property (and, where appropriate, `from_tokens`):

```pycon
>>> from pydantic_json_patch import CopyOp
>>> op = CopyOp.model_validate_json('{"op":"copy","path":"/foo/bar~1new","from":"/foo/bar~0old"}')
>>> op
CopyOp(op='copy', path='/foo/bar~1new', from_='/foo/bar~0old')
>>> op.path_tokens
('foo', 'bar/new')
>>> op.from_tokens
('foo', 'bar~old')
```

Similarly, the `create` factory methods can accept tuples of tokens, and will encode them appropriately:

```pycon
>>> from pydantic_json_patch import TestOp
>>> op = TestOp.create(path=("annotations", "scope/value"), value=None)
>>> op
TestOp(op='test', path='/annotations/scope~1value', value=None)
>>> op.model_dump_json()
'{"op":"test","path":"/annotations/scope~1value","value":null}'
```

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
  [json pointer]: https://datatracker.ietf.org/doc/html/rfc6901/
  [pydantic]: https://docs.pydantic.dev/latest/
