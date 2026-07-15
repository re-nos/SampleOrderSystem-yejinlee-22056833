import os

import pytest

from sample_order_system.controllers.production_controller import ProductionController
from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.production_queue import ProductionQueueEntry
from sample_order_system.models.sample import Sample
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.production_queue_repository import (
    ProductionQueueRepository,
)
from sample_order_system.repository.sample_repository import SampleRepository


@pytest.fixture
def order_repo(tmp_path):
    repo = OrderRepository(file_path=os.path.join(tmp_path, "order.json"))
    for order_id in ("O001", "O002"):
        repo.add(
            Order(
                order_id=order_id,
                sample_id="S001",
                customer_name="고객A",
                quantity=10,
                status=OrderStatus.PRODUCING,
                created_at="2026-07-15T10:00:00",
            )
        )
    return repo


@pytest.fixture
def inventory_repo(tmp_path):
    repo = InventoryRepository(file_path=os.path.join(tmp_path, "inventory.json"))
    repo.add(InventoryRecord(sample_id="S001", quantity=0))
    return repo


@pytest.fixture
def sample_repo(tmp_path):
    repo = SampleRepository(file_path=os.path.join(tmp_path, "sample.json"))
    repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.0, yield_rate=0.4))
    return repo


@pytest.fixture
def production_queue_repo(tmp_path):
    repo = ProductionQueueRepository(file_path=os.path.join(tmp_path, "production_queue.json"))
    repo.add(
        ProductionQueueEntry(
            order_id="O001", sample_id="S001", shortfall=10,
            actual_production_qty=15, total_production_turns=5, remaining_turns=5,
        )
    )
    repo.add(
        ProductionQueueEntry(
            order_id="O002", sample_id="S001", shortfall=8,
            actual_production_qty=8, total_production_turns=3, remaining_turns=3,
        )
    )
    return repo


@pytest.fixture
def controller(order_repo, inventory_repo, production_queue_repo, sample_repo):
    return ProductionController(
        order_repo=order_repo,
        inventory_repo=inventory_repo,
        production_queue_repo=production_queue_repo,
        sample_repo=sample_repo,
    )


def test_advance_turns_partial_progress_does_not_complete(controller, production_queue_repo):
    completed = controller.advance_turns(3)

    assert completed == []
    assert production_queue_repo.get("O001").remaining_turns == 2


def test_advance_turns_exact_completion(controller, order_repo, inventory_repo):
    completed = controller.advance_turns(5)

    assert [o.order_id for o in completed] == ["O001"]
    assert order_repo.get("O001").status is OrderStatus.CONFIRMED
    # leftover = actual_production_qty(15) - shortfall(10) = 5
    assert inventory_repo.get("S001").quantity == 5


def test_advance_turns_spillover_completes_multiple_jobs(controller, order_repo, production_queue_repo):
    completed = controller.advance_turns(8)  # O001(5) 완료 후 남은 3턴이 O002(3)로 이월되어 완료

    assert [o.order_id for o in completed] == ["O001", "O002"]
    assert order_repo.get("O002").status is OrderStatus.CONFIRMED
    assert production_queue_repo.list() == []


def test_current_job_returns_front_of_queue(controller):
    job = controller.current_job()

    assert job.order_id == "O001"


def test_waiting_jobs_excludes_current_job(controller):
    waiting = controller.waiting_jobs()

    assert [j.order_id for j in waiting] == ["O002"]


def test_current_job_returns_none_when_queue_empty(order_repo, inventory_repo, sample_repo, tmp_path):
    empty_queue_repo = ProductionQueueRepository(
        file_path=os.path.join(tmp_path, "empty_queue.json")
    )
    controller = ProductionController(
        order_repo=order_repo,
        inventory_repo=inventory_repo,
        production_queue_repo=empty_queue_repo,
        sample_repo=sample_repo,
    )

    assert controller.current_job() is None
    assert controller.waiting_jobs() == []


def test_current_job_detail_combines_order_and_sample_info(controller):
    detail = controller.current_job_detail()

    assert detail.order_id == "O001"
    assert detail.sample_name == "시료A"
    assert detail.order_quantity == 10
    assert detail.inventory_at_approval == 0  # order_quantity(10) - shortfall(10)
    assert detail.shortfall == 10
    assert detail.actual_production_qty == 15
    assert detail.yield_rate == 0.4
    assert detail.remaining_turns == 5


def test_current_job_detail_none_when_queue_empty(order_repo, inventory_repo, sample_repo, tmp_path):
    empty_queue_repo = ProductionQueueRepository(
        file_path=os.path.join(tmp_path, "empty_queue.json")
    )
    controller = ProductionController(
        order_repo=order_repo,
        inventory_repo=inventory_repo,
        production_queue_repo=empty_queue_repo,
        sample_repo=sample_repo,
    )

    assert controller.current_job_detail() is None


def test_waiting_job_details_excludes_current_job(controller):
    details = controller.waiting_job_details()

    assert [d.order_id for d in details] == ["O002"]
