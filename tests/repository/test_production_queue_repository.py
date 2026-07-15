import os

import pytest

from sample_order_system.common.exceptions import NotFoundError
from sample_order_system.models.production_queue import ProductionQueueEntry
from sample_order_system.repository.production_queue_repository import (
    ProductionQueueRepository,
)


@pytest.fixture
def repository(tmp_path):
    return ProductionQueueRepository(file_path=os.path.join(tmp_path, "production_queue.json"))


def test_add_and_list_preserves_fifo_order(repository):
    first = ProductionQueueEntry(
        order_id="O001", sample_id="S001", shortfall=10,
        actual_production_qty=25, total_production_turns=10, remaining_turns=10,
    )
    second = ProductionQueueEntry(
        order_id="O002", sample_id="S002", shortfall=5,
        actual_production_qty=10, total_production_turns=4, remaining_turns=4,
    )

    repository.add(first)
    repository.add(second)

    assert repository.list() == [first, second]


def test_delete_by_order_id(repository):
    repository.add(
        ProductionQueueEntry(
            order_id="O001", sample_id="S001", shortfall=10,
            actual_production_qty=25, total_production_turns=10, remaining_turns=10,
        )
    )

    repository.delete("O001")

    assert repository.list() == []


def test_get_missing_raises_not_found_error(repository):
    with pytest.raises(NotFoundError):
        repository.get("MISSING")
