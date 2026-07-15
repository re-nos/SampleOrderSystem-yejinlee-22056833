import os
from math import ceil

import pytest

from sample_order_system.common.exceptions import InvalidStateTransitionError
from sample_order_system.controllers.approval_controller import ApprovalController
from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.sample import Sample
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.production_queue_repository import (
    ProductionQueueRepository,
)
from sample_order_system.repository.sample_repository import SampleRepository


@pytest.fixture
def sample_repo(tmp_path):
    repo = SampleRepository(file_path=os.path.join(tmp_path, "sample.json"))
    repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.0, yield_rate=0.4))
    return repo


@pytest.fixture
def inventory_repo(tmp_path):
    repo = InventoryRepository(file_path=os.path.join(tmp_path, "inventory.json"))
    repo.add(InventoryRecord(sample_id="S001", quantity=0))
    return repo


@pytest.fixture
def order_repo(tmp_path):
    return OrderRepository(file_path=os.path.join(tmp_path, "order.json"))


@pytest.fixture
def production_queue_repo(tmp_path):
    return ProductionQueueRepository(file_path=os.path.join(tmp_path, "production_queue.json"))


@pytest.fixture
def controller(sample_repo, order_repo, inventory_repo, production_queue_repo):
    return ApprovalController(
        sample_repo=sample_repo,
        order_repo=order_repo,
        inventory_repo=inventory_repo,
        production_queue_repo=production_queue_repo,
    )


def _reserved_order(order_repo, order_id="O001", quantity=10):
    order = Order(
        order_id=order_id,
        sample_id="S001",
        customer_name="고객A",
        quantity=quantity,
        status=OrderStatus.RESERVED,
        created_at="2026-07-15T10:00:00",
    )
    return order_repo.add(order)


def test_approve_with_sufficient_stock_confirms_immediately(
    controller, order_repo, inventory_repo
):
    inventory_repo.update(InventoryRecord(sample_id="S001", quantity=10))
    _reserved_order(order_repo, quantity=10)

    result = controller.approve("O001")

    assert result.status is OrderStatus.CONFIRMED
    assert inventory_repo.get("S001").quantity == 0


def test_approve_with_insufficient_stock_starts_production(
    controller, order_repo, inventory_repo, production_queue_repo
):
    inventory_repo.update(InventoryRecord(sample_id="S001", quantity=0))
    _reserved_order(order_repo, quantity=10)

    result = controller.approve("O001")

    assert result.status is OrderStatus.PRODUCING
    assert inventory_repo.get("S001").quantity == 0

    entry = production_queue_repo.get("O001")
    assert entry.shortfall == 10
    assert entry.actual_production_qty == ceil(10 / 0.4)  # 25
    assert entry.total_production_turns == ceil(3.0 * 25)  # 75
    assert entry.remaining_turns == entry.total_production_turns


def test_approve_partial_stock_shortfall_calculation(controller, order_repo, inventory_repo):
    inventory_repo.update(InventoryRecord(sample_id="S001", quantity=4))
    _reserved_order(order_repo, quantity=10)

    controller.approve("O001")

    assert inventory_repo.get("S001").quantity == 0


def test_reject_sets_rejected_status(controller, order_repo):
    _reserved_order(order_repo)

    result = controller.reject("O001")

    assert result.status is OrderStatus.REJECTED


def test_approve_non_reserved_order_raises_invalid_state_transition_error(controller, order_repo):
    _reserved_order(order_repo)
    controller.reject("O001")

    with pytest.raises(InvalidStateTransitionError):
        controller.approve("O001")


def test_reject_non_reserved_order_raises_invalid_state_transition_error(
    controller, order_repo, inventory_repo
):
    inventory_repo.update(InventoryRecord(sample_id="S001", quantity=10))
    _reserved_order(order_repo)
    controller.approve("O001")

    with pytest.raises(InvalidStateTransitionError):
        controller.reject("O001")
