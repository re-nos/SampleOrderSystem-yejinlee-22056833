import os

import pytest

from sample_order_system.common.exceptions import InvalidStateTransitionError
from sample_order_system.controllers.shipment_controller import ShipmentController
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.repository.order_repository import OrderRepository


@pytest.fixture
def order_repo(tmp_path):
    return OrderRepository(file_path=os.path.join(tmp_path, "order.json"))


@pytest.fixture
def controller(order_repo):
    return ShipmentController(order_repo=order_repo)


def _order(order_id, status):
    return Order(
        order_id=order_id,
        sample_id="S001",
        customer_name="고객A",
        quantity=5,
        status=status,
        created_at="2026-07-15T10:00:00",
    )


def test_release_confirmed_order(controller, order_repo):
    order_repo.add(_order("O001", OrderStatus.CONFIRMED))

    result = controller.release("O001")

    assert result.status is OrderStatus.RELEASE
    assert order_repo.get("O001").status is OrderStatus.RELEASE


def test_release_reserved_order_raises(controller, order_repo):
    order_repo.add(_order("O001", OrderStatus.RESERVED))

    with pytest.raises(InvalidStateTransitionError):
        controller.release("O001")


def test_release_producing_order_raises(controller, order_repo):
    order_repo.add(_order("O001", OrderStatus.PRODUCING))

    with pytest.raises(InvalidStateTransitionError):
        controller.release("O001")


def test_release_twice_raises(controller, order_repo):
    order_repo.add(_order("O001", OrderStatus.CONFIRMED))
    controller.release("O001")

    with pytest.raises(InvalidStateTransitionError):
        controller.release("O001")


def test_list_releasable_orders_returns_only_confirmed(controller, order_repo):
    order_repo.add(_order("O001", OrderStatus.CONFIRMED))
    order_repo.add(_order("O002", OrderStatus.RESERVED))
    order_repo.add(_order("O003", OrderStatus.CONFIRMED))

    releasable = controller.list_releasable_orders()

    assert [o.order_id for o in releasable] == ["O001", "O003"]


def test_list_releasable_orders_empty_when_none_confirmed(controller):
    assert controller.list_releasable_orders() == []
