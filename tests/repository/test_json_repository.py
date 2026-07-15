import os
from dataclasses import dataclass
from enum import Enum

import pytest

from sample_order_system.common.exceptions import NotFoundError, ValidationError
from sample_order_system.repository.json_repository import JsonRepository


class WidgetStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass
class Widget:
    widget_id: str
    name: str
    status: WidgetStatus


@pytest.fixture
def repository(tmp_path):
    file_path = os.path.join(tmp_path, "widget.json")
    return JsonRepository(file_path=file_path, entity_type=Widget, id_field="widget_id")


def test_add_and_get(repository):
    widget = Widget(widget_id="W1", name="위젯1", status=WidgetStatus.ACTIVE)

    repository.add(widget)
    found = repository.get("W1")

    assert found == widget


def test_add_persists_enum_as_json_serializable_value(repository):
    widget = Widget(widget_id="W1", name="위젯1", status=WidgetStatus.ACTIVE)
    repository.add(widget)

    raw_records = repository._load()

    assert raw_records == [{"widget_id": "W1", "name": "위젯1", "status": "ACTIVE"}]


def test_add_duplicate_id_raises_validation_error(repository):
    widget = Widget(widget_id="W1", name="위젯1", status=WidgetStatus.ACTIVE)
    repository.add(widget)

    with pytest.raises(ValidationError):
        repository.add(widget)


def test_get_missing_raises_not_found_error(repository):
    with pytest.raises(NotFoundError):
        repository.get("MISSING")


def test_list_returns_all_entities(repository):
    repository.add(Widget(widget_id="W1", name="위젯1", status=WidgetStatus.ACTIVE))
    repository.add(Widget(widget_id="W2", name="위젯2", status=WidgetStatus.INACTIVE))

    result = repository.list()

    assert result == [
        Widget(widget_id="W1", name="위젯1", status=WidgetStatus.ACTIVE),
        Widget(widget_id="W2", name="위젯2", status=WidgetStatus.INACTIVE),
    ]


def test_update_existing_entity(repository):
    repository.add(Widget(widget_id="W1", name="위젯1", status=WidgetStatus.ACTIVE))

    repository.update(Widget(widget_id="W1", name="위젯1-수정", status=WidgetStatus.INACTIVE))

    assert repository.get("W1") == Widget(
        widget_id="W1", name="위젯1-수정", status=WidgetStatus.INACTIVE
    )


def test_update_missing_raises_not_found_error(repository):
    with pytest.raises(NotFoundError):
        repository.update(Widget(widget_id="MISSING", name="x", status=WidgetStatus.ACTIVE))


def test_delete_existing_entity(repository):
    repository.add(Widget(widget_id="W1", name="위젯1", status=WidgetStatus.ACTIVE))

    repository.delete("W1")

    assert repository.list() == []


def test_delete_missing_raises_not_found_error(repository):
    with pytest.raises(NotFoundError):
        repository.delete("MISSING")
