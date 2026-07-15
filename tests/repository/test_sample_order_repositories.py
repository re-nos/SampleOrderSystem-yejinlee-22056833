import os

import pytest

from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.sample import Sample
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.sample_repository import SampleRepository


@pytest.fixture
def sample_repository(tmp_path):
    return SampleRepository(file_path=os.path.join(tmp_path, "sample.json"))


@pytest.fixture
def order_repository(tmp_path):
    return OrderRepository(file_path=os.path.join(tmp_path, "order.json"))


def test_sample_repository_crud(sample_repository):
    sample = Sample(sample_id="S001", name="시료A", avg_production_time=3, yield_rate=0.8)

    sample_repository.add(sample)

    assert sample_repository.get("S001") == sample
    assert sample_repository.list() == [sample]


def test_order_repository_crud_with_status_enum(order_repository):
    order = Order(
        order_id="O001",
        sample_id="S001",
        customer_name="고객A",
        quantity=10,
        status=OrderStatus.RESERVED,
        created_at="2026-07-15T10:00:00",
    )

    order_repository.add(order)
    found = order_repository.get("O001")

    assert found == order
    assert found.status is OrderStatus.RESERVED
