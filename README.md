# Pydantic JSON Patch

[![Python uv CI][ci-badge]][ci-page]
[![Coverage Status][coverage-badge]][coverage-page]
[![PyPI - Version][pypi-badge]][pypi-page]

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

The operations that take a value (`AddOp`, `ReplaceOp`, and `TestOp`) are generic, so you can parameterize them with a specific value type:

```python
>>> from pydantic_json_patch import ReplaceOp
>>> op = ReplaceOp[str].create(path="/foo/bar", value="hello")
>>> op
ReplaceOp[str](op='replace', path='/foo/bar', value='hello')

```

Additionally, there are two compound types:

- `Operation` is the union of all the operations; and
- `JsonPatch` is a Pydantic `RootModel` representing a sequence of operations.

`JsonPatch` can be used directly for validation:

```python
>>> from pydantic_json_patch import JsonPatch
>>> patch = JsonPatch.model_validate_json('[{"op":"add","path":"/a/b/c","value":"foo"}]')
>>> patch[0]
AddOp(op='add', path='/a/b/c', value='foo')

```

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

Similarly, the `create` factory methods can accept sequences of tokens, and will encode them appropriately:

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

### Value type validation

You can also use a more specific type to apply type validation to the value properties:

```python
import typing as tp
from uuid import UUID

from fastapi import Body, FastAPI
from pydantic import Discriminator

from pydantic_json_patch import AddOp, TestOp

app = FastAPI()


@app.patch("/resource/{resource_id}")
def _(
    resource_id: UUID,
    operations: tp.Annotated[list[tp.Annotated[AddOp[int] | TestOp[int], Discriminator("op")]], Body()],
) -> ...:
    ...
```

**Note**: explicitly specifying the [discriminator][pydantic-discriminator] gives better results on _failed_ validation for unions of operations.

## Development

This project uses [uv] for managing dependencies.
Having installed uv, you can set the project up for local development with:

```shell
uv sync
uv run pre-commit install
```

The pre-commit hooks will ensure that the code style checks (using [isort] and [ruff]) are applied.

### Testing

The test suite uses [pytest] and can be run with:

```shell
uv run pytest
```

Additionally, there is [ty] type-checking that can be run with:

```shell
uv run ty check
```

### FastAPI

You can preview the FastAPI/Swagger documentation by running:

```shell
uv run fastapi dev tests/app.py
```

and visiting the Documentation link that's logged in the console.
This will auto-restart as you make changes.

  [ci-badge]: https://github.com/textbook/pydantic_json_patch/actions/workflows/push.yml/badge.svg
  [ci-page]: https://github.com/textbook/pydantic_json_patch/actions/workflows/push.yml
  [coverage-badge]: https://coveralls.io/repos/github/textbook/pydantic_json_patch/badge.svg?branch=main
  [coverage-page]: https://coveralls.io/github/textbook/pydantic_json_patch?branch=main
  [fastapi]: https://fastapi.tiangolo.com/
  [isort]: https://pycqa.github.io/isort/
  [json patch]: https://datatracker.ietf.org/doc/html/rfc6902/
  [json pointer]: https://datatracker.ietf.org/doc/html/rfc6901/
  [pydantic]: https://docs.pydantic.dev/latest/
  [pydantic-discriminator]: https://docs.pydantic.dev/latest/concepts/unions/#discriminated-unions-with-str-discriminators
  [pypi]: https://pypi.org/
  [pypi-badge]: https://img.shields.io/pypi/v/pydantic-json-patch?logo=python&logoColor=white&label=PyPI
  [pypi-page]: https://pypi.org/project/pydantic-json-patch/
  [pytest]: https://docs.pytest.org/en/stable/
  [ruff]: https://docs.astral.sh/ruff/
  [swagger-example]: https://github.com/textbook/pydantic_json_patch/blob/main/docs/swagger-example.png?raw=true
  [swagger-schemas]: https://github.com/textbook/pydantic_json_patch/blob/main/docs/swagger-schemas.png?raw=true
  [ty]: https://docs.astral.sh/ty/
  [uv]: https://docs.astral.sh/uv/
