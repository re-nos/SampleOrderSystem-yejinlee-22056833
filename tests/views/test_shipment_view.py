from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.views import colors
from sample_order_system.views.shipment_view import (
    format_release_result,
    format_releasable_orders,
)


def test_format_release_result_includes_order_info():
    order = Order(
        order_id="O001",
        sample_id="S001",
        customer_name="고객A",
        quantity=5,
        status=OrderStatus.RELEASE,
        created_at="2026-07-15T10:00:00",
    )

    result = format_release_result(order)

    assert "O001" in result
    assert "RELEASE" in result


def test_format_release_result_colors_status():
    order = Order(
        order_id="O001",
        sample_id="S001",
        customer_name="고객A",
        quantity=5,
        status=OrderStatus.RELEASE,
        created_at="2026-07-15T10:00:00",
    )

    result = format_release_result(order)

    assert colors.order_status_color("RELEASE") + "RELEASE" in result


def test_format_releasable_orders_empty_shows_guidance_message():
    result = format_releasable_orders([])

    assert "없습니다" in result


def test_format_releasable_orders_numbers_each_row():
    orders = [
        Order(
            order_id="O001",
            sample_id="S001",
            customer_name="고객A",
            quantity=5,
            status=OrderStatus.CONFIRMED,
            created_at="2026-07-15T10:00:00",
        ),
        Order(
            order_id="O002",
            sample_id="S001",
            customer_name="고객B",
            quantity=3,
            status=OrderStatus.CONFIRMED,
            created_at="2026-07-15T10:00:00",
        ),
    ]

    result = format_releasable_orders(orders)

    assert "[1]" in result
    assert "[2]" in result
    assert "O001" in result
    assert "고객B" in result
    assert "5 ea" in result
