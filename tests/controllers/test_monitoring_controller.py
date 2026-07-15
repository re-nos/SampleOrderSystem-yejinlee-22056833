import os

import pytest

from sample_order_system.controllers.monitoring_controller import MonitoringController
from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.sample import Sample
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.sample_repository import SampleRepository


@pytest.fixture
def sample_repo(tmp_path):
    return SampleRepository(file_path=os.path.join(tmp_path, "sample.json"))


@pytest.fixture
def inventory_repo(tmp_path):
    return InventoryRepository(file_path=os.path.join(tmp_path, "inventory.json"))


@pytest.fixture
def order_repo(tmp_path):
    return OrderRepository(file_path=os.path.join(tmp_path, "order.json"))


@pytest.fixture
def controller(sample_repo, inventory_repo, order_repo):
    return MonitoringController(
        sample_repo=sample_repo, inventory_repo=inventory_repo, order_repo=order_repo
    )


def _order(order_id, sample_id, quantity, status):
    return Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name="고객A",
        quantity=quantity,
        status=status,
        created_at="2026-07-15T10:00:00",
    )


def test_count_by_status_excludes_rejected_and_counts_each_status(controller, order_repo):
    order_repo.add(_order("O001", "S001", 5, OrderStatus.RESERVED))
    order_repo.add(_order("O002", "S001", 5, OrderStatus.REJECTED))
    order_repo.add(_order("O003", "S001", 5, OrderStatus.PRODUCING))
    order_repo.add(_order("O004", "S001", 5, OrderStatus.CONFIRMED))
    order_repo.add(_order("O005", "S001", 5, OrderStatus.RELEASE))

    counts = controller.count_by_status()

    assert counts == {"RESERVED": 1, "PRODUCING": 1, "CONFIRMED": 1, "RELEASE": 1}
    assert "REJECTED" not in counts


def test_count_by_status_all_zero_when_no_orders(controller):
    assert controller.count_by_status() == {
        "RESERVED": 0,
        "PRODUCING": 0,
        "CONFIRMED": 0,
        "RELEASE": 0,
    }


def test_stock_status_depleted_when_zero_quantity(controller, sample_repo, inventory_repo):
    sample_repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.0, yield_rate=0.5))
    inventory_repo.add(InventoryRecord(sample_id="S001", quantity=0))

    [status] = controller.stock_status()

    assert status.status == "고갈"
    assert status.remaining_ratio == 0.0


def test_stock_status_sufficient_when_no_demand(controller, sample_repo, inventory_repo):
    sample_repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.0, yield_rate=0.5))
    inventory_repo.add(InventoryRecord(sample_id="S001", quantity=10))

    [status] = controller.stock_status()

    assert status.status == "여유"
    assert status.remaining_ratio == 100.0


def test_stock_status_shortage_when_demand_exceeds_stock(
    controller, sample_repo, inventory_repo, order_repo
):
    sample_repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.0, yield_rate=0.5))
    inventory_repo.add(InventoryRecord(sample_id="S001", quantity=4))
    order_repo.add(_order("O001", "S001", 10, OrderStatus.RESERVED))

    [status] = controller.stock_status()

    assert status.status == "부족"
    assert status.remaining_ratio == 40.0


def test_stock_status_sufficient_when_stock_covers_demand(
    controller, sample_repo, inventory_repo, order_repo
):
    sample_repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.0, yield_rate=0.5))
    inventory_repo.add(InventoryRecord(sample_id="S001", quantity=20))
    order_repo.add(_order("O001", "S001", 10, OrderStatus.RESERVED))

    [status] = controller.stock_status()

    assert status.status == "여유"
    assert status.remaining_ratio == 100.0


def test_stock_status_only_counts_reserved_orders_as_demand(
    controller, sample_repo, inventory_repo, order_repo
):
    sample_repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.0, yield_rate=0.5))
    inventory_repo.add(InventoryRecord(sample_id="S001", quantity=4))
    order_repo.add(_order("O001", "S001", 100, OrderStatus.CONFIRMED))

    [status] = controller.stock_status()

    assert status.status == "여유"
    assert status.remaining_ratio == 100.0


def test_stock_status_returns_one_entry_per_sample(controller, sample_repo, inventory_repo):
    sample_repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.0, yield_rate=0.5))
    sample_repo.add(Sample(sample_id="S002", name="시료B", avg_production_time=2.0, yield_rate=0.9))
    inventory_repo.add(InventoryRecord(sample_id="S001", quantity=0))
    inventory_repo.add(InventoryRecord(sample_id="S002", quantity=10))

    statuses = controller.stock_status()

    assert {s.sample_id for s in statuses} == {"S001", "S002"}
