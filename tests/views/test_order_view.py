from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.sample import SampleSummary
from sample_order_system.views import colors
from sample_order_system.views.order_view import (
    format_order_cancelled,
    format_order_confirmation,
    format_order_registration_success,
)


def test_format_order_registration_success_includes_order_info():
    order = Order(
        order_id="O001",
        sample_id="S001",
        customer_name="고객A",
        quantity=10,
        status=OrderStatus.RESERVED,
        created_at="2026-07-15T10:00:00",
    )

    result = format_order_registration_success(order)

    assert "O001" in result
    assert "RESERVED" in result


def test_format_order_registration_success_colors_status_by_order_status():
    order = Order(
        order_id="O001",
        sample_id="S001",
        customer_name="고객A",
        quantity=10,
        status=OrderStatus.RESERVED,
        created_at="2026-07-15T10:00:00",
    )

    result = format_order_registration_success(order)

    assert colors.order_status_color("RESERVED") + "RESERVED" in result


def test_format_order_confirmation_includes_sample_customer_quantity():
    sample = SampleSummary(
        sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8, quantity=5
    )

    result = format_order_confirmation(sample, "고객A", 10)

    assert "시료A" in result
    assert "S001" in result
    assert "고객A" in result
    assert "10" in result


def test_format_order_cancelled_mentions_cancellation():
    result = format_order_cancelled()

    assert "취소" in result
