import json
import os

import pytest

from sample_order_system.storage.json_file_storage import read_json, write_json


def test_read_json_returns_empty_list_when_file_missing(tmp_path):
    file_path = os.path.join(tmp_path, "missing.json")

    assert read_json(file_path) == []


def test_write_then_read_round_trip(tmp_path):
    file_path = os.path.join(tmp_path, "sample.json")
    data = [{"sample_id": "S001", "name": "시료A"}]

    write_json(file_path, data)

    assert read_json(file_path) == data


def test_write_json_creates_parent_directory(tmp_path):
    file_path = os.path.join(tmp_path, "nested", "dir", "sample.json")

    write_json(file_path, [{"a": 1}])

    assert os.path.exists(file_path)
    assert read_json(file_path) == [{"a": 1}]


def test_write_json_overwrites_existing_content(tmp_path):
    file_path = os.path.join(tmp_path, "sample.json")
    write_json(file_path, [{"a": 1}])

    write_json(file_path, [{"a": 2}])

    assert read_json(file_path) == [{"a": 2}]


def test_write_json_does_not_corrupt_original_file_on_failure(tmp_path, monkeypatch):
    file_path = os.path.join(tmp_path, "sample.json")
    write_json(file_path, [{"a": 1}])

    def broken_dump(*args, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(json, "dump", broken_dump)

    with pytest.raises(ValueError):
        write_json(file_path, [{"a": 2}])

    monkeypatch.undo()
    assert read_json(file_path) == [{"a": 1}]

    leftover_tmp_files = [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]
    assert leftover_tmp_files == []
