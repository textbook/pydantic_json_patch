import typing as tp
from http import HTTPStatus
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

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
    "body, message",
    [
        pytest.param({}, "Input should be a valid list", id="not an array"),
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
            "String should match pattern '^(?:/(?:[^/~]|~[01])+)*$'",
            id="invalid path",
        ),
        pytest.param(
            [{"from": 123, "op": "copy", "path": "/a/path"}],
            "Input should be a valid string",
            id="invalid from",
        ),
    ],
)
def test_invalid_patch_rejected(test_client: TestClient, body: tp.Any, message: str):
    res = test_client.patch(f"/resource/{uuid4()}", json=body)
    assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert message in [detail["msg"] for detail in res.json()["detail"]]


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
