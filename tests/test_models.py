import json
import typing as tp
from collections.abc import Sequence

import pytest
from pydantic import ValidationError

from pydantic_json_patch import AddOp, CopyOp, MoveOp, RemoveOp, ReplaceOp, TestOp


def test_add_op_can_be_parsed():
    op: tp.Literal["add"] = "add"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps(dict(op=op, path=path, value=value))
    assert AddOp.model_validate_json(json_) == AddOp(op=op, path=path, value=value)


def test_add_op_can_be_created():
    path = "/foo/bar"
    value = 123
    assert AddOp.create(path=path, value=value) == AddOp(
        op="add", path=path, value=value
    )


def test_copy_op_can_be_parsed():
    op: tp.Literal["copy"] = "copy"
    path = "/foo/bar"
    from_ = "/baz/qux"
    json_ = json.dumps({"from": from_, "op": op, "path": path})
    assert (
        CopyOp.model_validate_json(json_) == CopyOp(from_=from_, op=op, path=path)  # type: ignore[missing-argument,unknown-argument] -- ty can't follow the alias
    )


def test_copy_op_can_be_created():
    path = "/foo/bar"
    assert CopyOp.create(path=path, from_=()) == CopyOp(from_="", op="copy", path=path)  # type: ignore[missing-argument,unknown-argument] -- ty can't follow the alias


def test_move_op_can_be_parsed():
    op: tp.Literal["move"] = "move"
    path = "/foo/bar"
    from_ = "/baz/qux"
    json_ = json.dumps({"from": from_, "op": op, "path": path})
    assert (
        MoveOp.model_validate_json(json_) == MoveOp(from_=from_, op=op, path=path)  # type: ignore[missing-argument,unknown-argument] -- ty can't follow the alias
    )


def test_create_move_op_requires_kwargs():
    with pytest.raises(TypeError):
        MoveOp.create("/foo/bar", from_=["baz", "qux"])  # type: ignore[too-many-positional-arguments] -- for testing purposes


def test_remove_op_can_be_parsed():
    op: tp.Literal["remove"] = "remove"
    path = "/foo/bar"
    json_ = json.dumps(dict(op=op, path=path))
    assert RemoveOp.model_validate_json(json_) == RemoveOp(op=op, path=path)


@pytest.mark.parametrize(
    "tokens, path",
    [
        pytest.param("/foo/bar", "/foo/bar", id="string path"),
        pytest.param(("foo", "bar"), "/foo/bar", id="simple path"),
        pytest.param((), "", id="empty"),
        pytest.param(["foo~bar", "baz"], "/foo~0bar/baz", id="includes tilde"),
        pytest.param(("foo/bar", "baz"), "/foo~1bar/baz", id="includes slash"),
    ],
)
def test_remove_op_can_be_created(tokens: Sequence[str], path: str):
    op: RemoveOp = RemoveOp.create(path=tokens)
    assert op == RemoveOp(op="remove", path=path)


def test_create_remove_op_requires_kwargs():
    with pytest.raises(TypeError):
        RemoveOp.create(["foo", "bar", "baz"])  # type: ignore[too-many-positional-arguments] -- for testing purposes


def test_replace_op_can_be_parsed():
    op: tp.Literal["replace"] = "replace"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps(dict(op=op, path=path, value=value))
    assert ReplaceOp.model_validate_json(json_) == ReplaceOp(
        op=op, path=path, value=value
    )


def test_create_replace_op_requires_kwargs():
    with pytest.raises(TypeError):
        ReplaceOp.create("/foo/bar", value=["baz", "qux"])  # type: ignore[too-many-positional-arguments] -- for testing purposes


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


@pytest.mark.parametrize(
    "from_",
    [
        pytest.param("foo/bar", id="no leading slash"),
        pytest.param("//foo/bar", id="two consecutive slashes"),
        pytest.param("/foo/bar/", id="trailing slash"),
        pytest.param("/foo~bar", id="unescaped tilde"),
    ],
)
def test_invalid_from_is_not_allowed(from_: str):
    data = dict(from_=from_, op="copy", path="/foo/bar")
    with pytest.raises(ValidationError):
        CopyOp.model_validate(data)


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


@pytest.mark.parametrize(
    "path, tokens",
    [
        pytest.param("", (), id="empty path"),
        pytest.param("/foo/bar", ("foo", "bar"), id="simple path"),
        pytest.param("/foo~1bar", ("foo/bar",), id="includes slash"),
        pytest.param("/foo~0bar", ("foo~bar",), id="includes tilde"),
        pytest.param("/foo~0123~1bar", ("foo~123/bar",), id="includes both"),
    ],
)
def test_path_tokens_exposed(path: str, tokens: tuple[str, ...]):
    op = CopyOp(from_=path, op="copy", path=path)  # type: ignore[missing-argument,unknown-argument] -- ty can't follow the alias
    assert op.from_tokens == tokens
    assert op.path_tokens == tokens


def test_models_are_immutable():
    op = RemoveOp.create(path=["foo", "bar"])
    with pytest.raises(ValidationError, match="Instance is frozen"):
        op.op = "copy"  # type: ignore[invalid-assignment] -- for testing purposes
