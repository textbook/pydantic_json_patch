import json
import typing as tp

import pytest
from joythief.data_structures import DictContaining
from joythief.strings import StringMatching
from pydantic import ValidationError

from pydantic_json_patch import (
    AddOp,
    CopyOp,
    JsonPatch,
    MoveOp,
    RemoveOp,
    ReplaceOp,
    TestOp,
)


def test_add_op_can_be_parsed():
    op: tp.Literal["add"] = "add"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps({"op": op, "path": path, "value": value})
    assert AddOp.model_validate_json(json_) == AddOp(op=op, path=path, value=value)


def test_add_op_can_be_created():
    path = "/foo/bar"
    value = 123
    assert AddOp[int].create(path=path, value=value) == AddOp(
        op="add",
        path=path,
        value=value,
    )


def test_copy_op_can_be_parsed():
    op: tp.Literal["copy"] = "copy"
    path = "/foo/bar"
    from_ = "/baz/qux"
    json_ = json.dumps({"from": from_, "op": op, "path": path})
    assert (
        CopyOp.model_validate_json(json_) == CopyOp(from_=from_, op=op, path=path)  # ty: ignore[missing-argument,unknown-argument] -- ty can't follow the alias
    )


def test_copy_op_can_be_created():
    path = "/foo/bar"
    assert CopyOp.create(path=path, from_=()) == CopyOp(from_="", op="copy", path=path)  # ty: ignore[missing-argument,unknown-argument] -- ty can't follow the alias


def test_move_op_can_be_parsed():
    op: tp.Literal["move"] = "move"
    path = "/foo/bar"
    from_ = "/baz/qux"
    json_ = json.dumps({"from": from_, "op": op, "path": path})
    assert (
        MoveOp.model_validate_json(json_) == MoveOp(from_=from_, op=op, path=path)  # ty: ignore[missing-argument,unknown-argument] -- ty can't follow the alias
    )


def test_remove_op_can_be_parsed():
    op: tp.Literal["remove"] = "remove"
    path = "/foo/bar"
    json_ = json.dumps({"op": op, "path": path})
    assert RemoveOp.model_validate_json(json_) == RemoveOp(op=op, path=path)


@pytest.mark.parametrize(
    ("tokens", "path"),
    [
        pytest.param("/foo/bar", "/foo/bar", id="string path"),
        pytest.param(("foo", "bar"), "/foo/bar", id="simple path"),
        pytest.param((), "", id="empty"),
        pytest.param(("foo~bar", "baz"), "/foo~0bar/baz", id="includes tilde"),
        pytest.param(("foo/bar", "baz"), "/foo~1bar/baz", id="includes slash"),
    ],
)
def test_remove_op_can_be_created(tokens: str | tuple[str, ...], path: str):
    op: RemoveOp = RemoveOp.create(path=tokens)
    assert op == RemoveOp(op="remove", path=path)


def test_replace_op_can_be_parsed():
    op: tp.Literal["replace"] = "replace"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps({"op": op, "path": path, "value": value})
    assert ReplaceOp.model_validate_json(json_) == ReplaceOp(
        op=op,
        path=path,
        value=value,
    )


def test_test_op_can_be_parsed():
    op: tp.Literal["test"] = "test"
    path = "/foo/bar"
    value = 123
    json_ = json.dumps({"op": op, "path": path, "value": value})
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
    data = {"op": "remove", "path": path}
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
    data = {"from_": from_, "op": "copy", "path": "/foo/bar"}
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
    json_ = json.dumps(
        {"baz": "qux", "foo": "bar", "op": op, "path": path, "value": value}
    )
    assert TestOp.model_validate_json(json_) == TestOp(op=op, path=path, value=value)


@pytest.mark.parametrize(
    ("path", "tokens"),
    [
        pytest.param("", (), id="empty path"),
        pytest.param("/foo/bar", ("foo", "bar"), id="simple path"),
        pytest.param("/foo~1bar", ("foo/bar",), id="includes slash"),
        pytest.param("/foo~0bar", ("foo~bar",), id="includes tilde"),
        pytest.param("/foo~0123~1bar", ("foo~123/bar",), id="includes both"),
    ],
)
def test_path_tokens_exposed(path: str, tokens: tuple[str, ...]):
    op = CopyOp(from_=path, op="copy", path=path)  # ty: ignore[missing-argument,unknown-argument] -- ty can't follow the alias
    assert op.from_tokens == tokens
    assert op.path_tokens == tokens


def test_models_are_immutable():
    patch = JsonPatch(
        [TestOp[list[str]].create(path=("foo", "bar"), value=["baz", "qux"])],
    )
    with pytest.raises(ValidationError):
        patch.root = []
    with pytest.raises(ValidationError):
        patch[0].op = "copy"  # ty: ignore[invalid-assignment] -- testing that frozen model rejects assignment


def test_json_patch_can_be_parsed():
    json_ = """[
        {"op": "test", "path": "/a/b/c", "value": "foo"},
        {"op": "remove", "path": "/a/b/c"}
    ]"""
    result = JsonPatch.model_validate_json(json_)
    assert list(result) == [
        TestOp(op="test", path="/a/b/c", value="foo"),
        RemoveOp(op="remove", path="/a/b/c"),
    ]


def test_json_patch_round_trips():
    json_ = """[
        {"op": "test", "path": "/a/b/c", "value": "foo"},
        {"op": "remove", "path": "/a/b/c"}
    ]"""
    result = JsonPatch.model_validate_json(json_)
    assert result == JsonPatch.model_validate_json(result.model_dump_json())


@pytest.fixture(name="patch")
def _create_patch() -> JsonPatch:
    return JsonPatch(
        [AddOp[int].create(path="/foo", value=1), RemoveOp.create(path="/bar")],
    )


def test_json_patch_is_iterable(patch: JsonPatch):
    assert list(patch) == [
        AddOp[int].create(path="/foo", value=1),
        RemoveOp.create(path="/bar"),
    ]


def test_json_patch_has_length(patch: JsonPatch):
    assert len(patch) == 2


def test_json_patch_supports_indexing(patch: JsonPatch):
    assert patch[0] == AddOp[int].create(path="/foo", value=1)
    assert patch[1] == RemoveOp.create(path="/bar")


def test_json_patch_supports_contains(patch: JsonPatch):
    assert AddOp[int].create(path="/foo", value=1) in patch


def test_json_patch_supports_reversed(patch: JsonPatch):
    assert list(reversed(patch)) == [
        RemoveOp.create(path="/bar"),
        AddOp[int].create(path="/foo", value=1),
    ]


def test_json_patch_supports_index(patch: JsonPatch):
    assert patch.index(RemoveOp.create(path="/bar")) == 1


def test_json_patch_supports_count(patch: JsonPatch):
    assert patch.count(AddOp[int].create(path="/foo", value=1)) == 1


def test_json_patch_can_be_created_from_tuple():
    patch = JsonPatch((MoveOp.create(path="/foo", from_="/bar"),))
    assert len(patch) == 1


def test_json_patch_root_is_immutable():
    patch = JsonPatch([RemoveOp.create(path="/foo")])
    with pytest.raises(TypeError):
        patch.root[0] = RemoveOp.create(path="/bar")  # ty: ignore[invalid-assignment] -- testing that root rejects assignment


def test_parameterised_model_schema_is_sensible():
    assert TestOp[int].model_json_schema() == DictContaining(
        description=StringMatching(r"^Represents the \[test] operation\."),
        title="JsonPatchTestOperation[int]",
    )
