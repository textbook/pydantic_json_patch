# Pydantic JSON Patch

[![Python uv CI][ci-badge]][ci-page]
[![Coverage Status][coverage-badge]][coverage-page]

[Pydantic] models for implementing [JSON Patch].

## Installation

_Pydantic JSON Patch_ is published to [PyPI], and can be installed with e.g.:

```shell
pip install pydantic-json-patch
```

## Models

A model is provided for each of the six JSON Patch operations:

- `AddOp`
- `CopyOp`
- `MoveOp`
- `RemoveOp`
- `ReplaceOp`
- `TestOp`

As repeating the op is a bit awkward (`CopyOp(op="copy", ...)`), a `create` factory method is available:

```python
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

```python
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

```python
>>> from pydantic_json_patch import TestOp
>>> op = TestOp.create(path=("annotations", "scope/value"), value=None)
>>> op
TestOp(op='test', path='/annotations/scope~1value', value=None)
>>> op.model_dump_json()
'{"op":"test","path":"/annotations/scope~1value","value":null}'
```

## FastAPI

You can use this package to validate a JSON Patch endpoint in a FastAPI application, for example:

```python
import typing as tp
from uuid import UUID

from fastapi import Body, FastAPI

from pydantic_json_patch import JsonPatch

app = FastAPI()


@app.patch("/resource/{resource_id}")
def _(resource_id: UUID, operations: tp.Annotated[JsonPatch, Body()]) -> ...:
    ...
```

This will provide a sensible example of the request body:

[![Screenshot of Swagger UI request body example][swagger-example]][swagger-example]

and list the models along with the other schemas:

[![Screenshot of Swagger UI schema list][swagger-schemas]][swagger-schemas]

  [ci-badge]: https://github.com/textbook/pydantic_json_patch/actions/workflows/push.yml/badge.svg
  [ci-page]: https://github.com/textbook/pydantic_json_patch/actions/workflows/push.yml
  [coverage-badge]: https://coveralls.io/repos/github/textbook/pydantic_json_patch/badge.svg?branch=main
  [coverage-page]: https://coveralls.io/github/textbook/pydantic_json_patch?branch=main
  [fastapi]: https://fastapi.tiangolo.com/
  [json patch]: https://datatracker.ietf.org/doc/html/rfc6902/
  [json pointer]: https://datatracker.ietf.org/doc/html/rfc6901/
  [pydantic]: https://docs.pydantic.dev/latest/
  [pypi]: https://pypi.org/
  [swagger-example]: https://github.com/textbook/pydantic_json_patch/blob/main/docs/swagger-example.png?raw=true
  [swagger-schemas]: https://github.com/textbook/pydantic_json_patch/blob/main/docs/swagger-schemas.png?raw=true
