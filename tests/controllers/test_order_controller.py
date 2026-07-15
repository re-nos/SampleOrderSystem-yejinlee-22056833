import os

import pytest

from sample_order_system.common.exceptions import NotFoundError, ValidationError
from sample_order_system.controllers.order_controller import OrderController
from sample_order_system.models.order import OrderStatus
from sample_order_system.models.sample import Sample
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.sample_repository import SampleRepository


@pytest.fixture
def sample_repository(tmp_path):
    repo = SampleRepository(file_path=os.path.join(tmp_path, "sample.json"))
    repo.add(Sample(sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8))
    return repo


@pytest.fixture
def order_repository(tmp_path):
    return OrderRepository(file_path=os.path.join(tmp_path, "order.json"))


@pytest.fixture
def controller(sample_repository, order_repository):
    return OrderController(
        sample_repo=sample_repository,
        order_repo=order_repository,
        clock=lambda: "2026-07-15T10:00:00",
    )


def test_place_order_creates_reserved_order(controller):
    order = controller.place_order(sample_id="S001", customer_name="고객A", quantity=10)

    assert order.order_id == "O001"
    assert order.sample_id == "S001"
    assert order.customer_name == "고객A"
    assert order.quantity == 10
    assert order.status is OrderStatus.RESERVED
    assert order.created_at == "2026-07-15T10:00:00"


def test_place_order_persists_to_repository(controller, order_repository):
    order = controller.place_order(sample_id="S001", customer_name="고객A", quantity=10)

    assert order_repository.get(order.order_id) == order


def test_place_order_unknown_sample_raises_not_found_error(controller):
    with pytest.raises(NotFoundError):
        controller.place_order(sample_id="UNKNOWN", customer_name="고객A", quantity=10)


@pytest.mark.parametrize("quantity", [0, -1])
def test_place_order_non_positive_quantity_raises_validation_error(controller, quantity):
    with pytest.raises(ValidationError):
        controller.place_order(sample_id="S001", customer_name="고객A", quantity=quantity)


def test_place_order_increments_order_id(controller):
    first = controller.place_order(sample_id="S001", customer_name="고객A", quantity=1)
    second = controller.place_order(sample_id="S001", customer_name="고객B", quantity=2)

    assert first.order_id == "O001"
    assert second.order_id == "O002"
