import json
import os
import tempfile
from typing import List


def read_json(file_path: str) -> List[dict]:
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        return []

    return json.loads(content)


def write_json(file_path: str, data: List[dict]) -> None:
    directory = os.path.dirname(file_path) or "."
    os.makedirs(directory, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, file_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
