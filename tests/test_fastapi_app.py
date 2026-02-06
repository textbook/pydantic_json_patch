import typing as tp
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from .app import app


def test_empty_list_accepted(test_client: TestClient):
    res = test_client.patch("/test", json=[])
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
    res = test_client.patch("/test", json=example)
    assert res.status_code == HTTPStatus.OK
    assert res.json() == example


@pytest.mark.parametrize(
    "body",
    [
        pytest.param({}, id="not an array"),
        pytest.param([{"foo": "bar"}], id="not an operation"),
        pytest.param([{"op": "bar"}], id="not a known operation"),
        pytest.param(
            [{"op": "copy", "path": "/foo/bar", "value": 123}], id="invalid operation"
        ),
    ],
)
def test_invalid_patch_rejected(test_client: TestClient, body: tp.Any):
    res = test_client.patch("/test", json=body)
    assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


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
