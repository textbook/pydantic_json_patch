import pathlib
import sys

import pytest

from pydantic_json_patch import __version__


@pytest.mark.skipif(
    sys.version_info < (3, 11), reason="tomllib not available in Python 3.10"
)
def test_version_exposed():
    import tomllib  # type: ignore[unresolved-import] -- only runs in py3.10+

    with open(pathlib.Path(__file__).parent / ".." / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    assert data["project"]["version"] == __version__
