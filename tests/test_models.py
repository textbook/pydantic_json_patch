import json
import typing as tp

import pytest
from pydantic import ValidationError

from pydantic_json_patch import AddOp, RemoveOp, ReplaceOp, TestOp


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


def test_replace_op_can_be_parsed():
    op: tp.Literal["replace"] = "replace"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps(dict(op=op, path=path, value=value))
    assert ReplaceOp.model_validate_json(json_) == ReplaceOp(
        op=op, path=path, value=value
    )


def test_test_op_can_be_parsed():
    op: tp.Literal["test"] = "test"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps(dict(op=op, path=path, value=value))
    assert TestOp.model_validate_json(json_) == TestOp(op=op, path=path, value=value)


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


def test_additional_members_are_ignored():
    """Per the specification:

    Members that are not explicitly defined for the operation in
    question MUST be ignored (i.e., the operation will complete as if
    the undefined member did not appear in the object).

    """
    op: tp.Literal["test"] = "test"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps(dict(baz="qux", foo="bar", op=op, path=path, value=value))
    assert TestOp.model_validate_json(json_) == TestOp(op=op, path=path, value=value)
