from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.production_queue import ProductionQueueEntry
from sample_order_system.models.sample import Sample


def test_sample_fields():
    sample = Sample(sample_id="S001", name="시료A", avg_production_time=3, yield_rate=0.8)

    assert sample.sample_id == "S001"
    assert sample.name == "시료A"
    assert sample.avg_production_time == 3
    assert sample.yield_rate == 0.8


def test_order_fields_and_status_enum():
    order = Order(
        order_id="O001",
        sample_id="S001",
        customer_name="고객A",
        quantity=10,
        status=OrderStatus.RESERVED,
        created_at="2026-07-15T10:00:00",
    )

    assert order.status is OrderStatus.RESERVED
    assert OrderStatus.RESERVED.value == "RESERVED"


def test_order_status_has_all_prd_states():
    expected = {"RESERVED", "REJECTED", "PRODUCING", "CONFIRMED", "RELEASE"}
    actual = {status.value for status in OrderStatus}

    assert actual == expected


def test_inventory_record_fields():
    record = InventoryRecord(sample_id="S001", quantity=5)

    assert record.sample_id == "S001"
    assert record.quantity == 5


def test_production_queue_entry_fields():
    entry = ProductionQueueEntry(
        order_id="O001",
        sample_id="S001",
        actual_production_qty=7,
        total_production_turns=21,
        remaining_turns=15,
    )

    assert entry.actual_production_qty == 7
    assert entry.total_production_turns == 21
    assert entry.remaining_turns == 15
