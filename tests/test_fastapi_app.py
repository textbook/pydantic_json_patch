import typing as tp
from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from joythief.strings import StringMatching

from pydantic_json_patch import JsonPatch, TestOp

from .app import app


def test_empty_list_accepted(test_client: TestClient):
    res = test_client.patch(f"/resource/{uuid4()}", json=[])
    assert res.status_code == HTTPStatus.OK
    assert res.json() == []


def test_valid_operations_accepted(test_client: TestClient):
    example = [
        {"op": "test", "path": "/a/b/c", "value": "foo"},
        {"op": "remove", "path": "/a/b/c"},
        {"op": "add", "path": "/a/b/c", "value": ["foo", "bar"]},
        {"op": "replace", "path": "/a/b/c", "value": 42},
        {"op": "move", "from": "/a/b/c", "path": "/a/b/d"},
        {"op": "copy", "from": "/a/b/d", "path": "/a/b/e"},
    ]
    res = test_client.patch(f"/resource/{uuid4()}", json=example)
    assert res.status_code == HTTPStatus.OK
    assert res.json() == example


@pytest.mark.parametrize(
    ("body", "message"),
    [
        pytest.param({}, "Input should be an instance of Sequence", id="not an array"),
        pytest.param(
            [{"foo": "bar"}],
            "Unable to extract tag using discriminator 'op'",
            id="not an operation",
        ),
        pytest.param(
            [{"op": "bar"}],
            "Input tag 'bar' found using 'op' does not match any of the expected tags: "
            "'add', 'copy', 'move', 'remove', 'replace', 'test'",
            id="not a known operation",
        ),
        pytest.param(
            [{"op": "copy", "path": "/foo/bar", "value": 123}],
            "Field required",
            id="invalid operation",
        ),
        pytest.param(
            [{"op": "test", "path": "not-a-path", "value": None}],
            StringMatching("^String should match pattern"),
            id="invalid path",
        ),
        pytest.param(
            [{"from": 123, "op": "copy", "path": "/a/path"}],
            "Input should be a valid string",
            id="invalid from",
        ),
    ],
)
def test_invalid_patch_rejected(
    test_client: TestClient, body: tp.Any, message: str | StringMatching
):
    res = test_client.patch(f"/resource/{uuid4()}", json=body)
    assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    (actual,) = [detail["msg"] for detail in res.json()["detail"]]
    assert message == actual


def test_models_can_be_used_to_validate_specific_op_types(test_client: TestClient):
    patch = JsonPatch([TestOp[str].create(path="/foo/bar", value="baz")])
    res = test_client.patch("/other_resource/123", json=patch.model_dump())
    assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert {"Input should be a valid integer"} == {
        detail["msg"] for detail in res.json()["detail"]
    }


def test_sensible_property_examples(test_client: TestClient):
    res = test_client.get("/openapi.json")
    document = res.json()
    for schema in document["components"]["schemas"].values():
        if schema["type"] == "object" and "op" in schema["properties"]:
            assert schema["properties"]["path"].get("examples") == ["/a/b/c"]
            if "from" in schema["properties"]:
                assert schema["properties"]["from"].get("examples") == ["/a/b/d"]
            if "value" in schema["properties"]:
                assert schema["properties"]["value"].get("examples") == [42]


@pytest.mark.parametrize("op", ["add", "copy", "move", "remove", "replace", "test"])
def test_sensible_titles(op: str, test_client: TestClient):
    res = test_client.get("/openapi.json")
    document = res.json()
    assert (
        document["components"]["schemas"][f"{op.capitalize()}Op"].get("title")
        == f"JsonPatch{op.capitalize()}Operation"
    )


@pytest.fixture(name="test_client")
def _create_test_client() -> TestClient:
    return TestClient(app=app)
