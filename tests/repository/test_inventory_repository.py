import os

import pytest

from sample_order_system.common.exceptions import NotFoundError
from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.repository.inventory_repository import InventoryRepository


@pytest.fixture
def inventory_repository(tmp_path):
    return InventoryRepository(file_path=os.path.join(tmp_path, "inventory.json"))


def test_add_and_get(inventory_repository):
    record = InventoryRecord(sample_id="S001", quantity=0)

    inventory_repository.add(record)

    assert inventory_repository.get("S001") == record


def test_update_quantity(inventory_repository):
    inventory_repository.add(InventoryRecord(sample_id="S001", quantity=0))

    inventory_repository.update(InventoryRecord(sample_id="S001", quantity=5))

    assert inventory_repository.get("S001").quantity == 5


def test_get_missing_raises_not_found_error(inventory_repository):
    with pytest.raises(NotFoundError):
        inventory_repository.get("MISSING")
