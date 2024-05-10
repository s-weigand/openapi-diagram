"""Module containing utility functions."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator
from typing import Literal

import yaml

Json = dict[str | Literal["anyOf", "type"], "Json"] | list["Json"] | str | bool


class UnsopportFileTypeError(ValueError):
    """Error raised when a file type isn't supported."""


def convert_3_dot_1_to_3_dot_0(json: dict[str, Json]):  # noqa: C901, DOC101, DOC109, DOC103
    """Attempt to convert version 3.1.0 of some openAPI json into 3.0.3.

    Ref.: https://github.com/tiangolo/fastapi/discussions/9789#discussioncomment-8629746

    Usage:

        >>> from pprint import pprint
        >>> json = {
        ...     "some_irrelevant_keys": {...},
        ...     "nested_dict": {"nested_key": {"anyOf": [{"type": "string"}, {"type": "null"}]}},
        ...     "examples": [{...}, {...}]
        ... }
        >>> convert_3_dot_1_to_3_dot_0(json)
        >>> pprint(json)
        {'example': {Ellipsis},
         'nested_dict': {'nested_key': {'anyOf': [{'type': 'string'}],
                                        'nullable': True}},
         'openapi': '3.0.3',
         'some_irrelevant_keys': {Ellipsis}}
    """
    json["openapi"] = "3.0.3"

    def inner(yaml_dict: Json):
        if isinstance(yaml_dict, dict):
            if "anyOf" in yaml_dict and isinstance((anyOf := yaml_dict["anyOf"]), list):  # noqa: N806
                for i, item in enumerate(anyOf):
                    if isinstance(item, dict) and item.get("type") == "null":
                        anyOf.pop(i)
                        yaml_dict["nullable"] = True
            if "examples" in yaml_dict:
                examples = yaml_dict["examples"]
                del yaml_dict["examples"]
                if isinstance(examples, list) and len(examples):
                    yaml_dict["example"] = examples[0]
            for value in yaml_dict.values():
                inner(value)
        elif isinstance(yaml_dict, list):
            for item in yaml_dict:
                inner(item)

    inner(json)


@contextmanager
def openapi_3_dot_1_compat(spec_file: Path) -> Generator[Path, None, None]:
    """Context manager to downgrade openapi 3.1 specs to 3.0 specs.

    Parameters
    ----------
    spec_file : Path
        Path to original spec file.

    Yields
    ------
    Path
        Path to temporary compat file.

    Raises
    ------
    ValueError
        If file format is not supported.
    """
    if spec_file.suffix == ".json":
        spec_data = json.loads(spec_file.read_text())
    elif spec_file.suffix in (".yaml", ".yml"):
        spec_data = yaml.safe_load(spec_file.read_text())
    else:
        msg = f"File type: *{spec_file.suffix} is not supported."
        raise UnsopportFileTypeError(msg)
    with TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "openapi_spec.json"
        if spec_data["openapi"].startswith("3.1"):
            convert_3_dot_1_to_3_dot_0(spec_data)
        tmp_file.write_text(json.dumps(spec_data))
        yield tmp_file
