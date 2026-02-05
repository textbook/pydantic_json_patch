import json

import pytest
from pydantic import ValidationError

from pydantic_json_patch import RemoveOp


def test_remove_op_can_be_parsed():
    data = dict(op="remove", path="/foo/bar")
    assert RemoveOp.model_validate_json(json.dumps(data)) == RemoveOp(**data)


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
