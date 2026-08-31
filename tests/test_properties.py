import typing as tp
from collections.abc import Callable

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from pydantic_json_patch import JsonPatch


@st.composite
def json_pointer(draw: Callable[..., tuple[str, ...]]) -> str:
    """Generate a valid RFC 6901 JSON Pointer."""
    parts = draw(st.tuples(st.text(st.characters(codec="utf-8"), min_size=1)))
    return "/".join(
        ["", *(part.replace("~", "~0").replace("/", "~1") for part in parts)]
    )


def json_value(*, finite_only: bool = False) -> st.SearchStrategy[tp.Any]:
    numbers = st.integers() | st.floats(
        allow_nan=not finite_only, allow_infinity=not finite_only
    )
    return st.recursive(
        st.none() | st.booleans() | st.text() | numbers,
        extend=lambda xs: st.lists(xs) | st.dictionaries(st.text(), xs),
    )


@st.composite
def json_patch_operation(draw: Callable[..., tp.Any]) -> dict[str, tp.Any]:
    op = {
        "op": draw(
            st.sampled_from(["add", "copy", "move", "remove", "replace", "test"])
        ),
        "path": draw(json_pointer()),
    }
    if op["op"] in {"add", "replace", "test"}:
        op.update({"value": draw(json_value())})
    elif op["op"] in {"copy", "move"}:
        op.update({"from": draw(json_pointer())})
    return op


@given(st.lists(json_value(), min_size=1))
def test_random_values(value: list[tp.Any]):
    with pytest.raises(ValidationError):
        JsonPatch.model_validate(value)


@given(st.lists(json_patch_operation()))
def test_valid_operations(ops: list[dict[str, tp.Any]]):
    JsonPatch.model_validate(ops)
