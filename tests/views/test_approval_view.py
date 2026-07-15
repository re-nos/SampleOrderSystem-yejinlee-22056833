from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.views import colors
from sample_order_system.views.approval_view import format_approval_result


def test_format_approval_result_confirmed():
    order = Order(
        order_id="O001",
        sample_id="S001",
        customer_name="고객A",
        quantity=10,
        status=OrderStatus.CONFIRMED,
        created_at="2026-07-15T10:00:00",
    )

    result = format_approval_result(order)

    assert "O001" in result
    assert "CONFIRMED" in result


def test_format_approval_result_producing():
    order = Order(
        order_id="O002",
        sample_id="S001",
        customer_name="고객B",
        quantity=10,
        status=OrderStatus.PRODUCING,
        created_at="2026-07-15T10:00:00",
    )

    result = format_approval_result(order)

    assert "O002" in result
    assert "PRODUCING" in result


def test_format_approval_result_colors_status():
    order = Order(
        order_id="O001",
        sample_id="S001",
        customer_name="고객A",
        quantity=10,
        status=OrderStatus.CONFIRMED,
        created_at="2026-07-15T10:00:00",
    )

    result = format_approval_result(order)

    assert colors.order_status_color("CONFIRMED") + "CONFIRMED" in result
