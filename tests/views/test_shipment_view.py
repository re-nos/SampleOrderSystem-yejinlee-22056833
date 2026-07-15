from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.views import colors
from sample_order_system.views.shipment_view import format_release_result


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
