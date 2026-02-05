import json
import typing as tp

import pytest
from pydantic import ValidationError

from pydantic_json_patch import AddOp, RemoveOp


def test_add_op_can_be_parsed():
    op: tp.Literal["add"] = "add"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps(dict(op=op, path=path, value=value))
    assert AddOp.model_validate_json(json_) == AddOp(op=op, path=path, value=value)


def test_remove_op_can_be_parsed():
    op: tp.Literal["remove"] = "remove"
    path = "/foo/bar"
    json_ = json.dumps(dict(op=op, path=path))
    assert RemoveOp.model_validate_json(json_) == RemoveOp(op=op, path=path)


@pytest.mark.parametrize(
    "path",
    [
        pytest.param("foo/bar", id="no leading slash"),
        pytest.param("//foo/bar", id="two consecutive slashes"),
        pytest.param("/foo/bar/", id="trailing slash"),
    ],
)
def test_invalid_path_is_not_allowed(path: str):
    data = dict(op="remove", path=path)
    with pytest.raises(ValidationError):
        RemoveOp.model_validate(data)
