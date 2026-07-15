from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.stock_check import StockCheck
from sample_order_system.views import colors
from sample_order_system.views.approval_view import (
    format_approval_result,
    format_pending_orders,
    format_stock_check,
)


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


def test_format_pending_orders_empty_shows_guidance_message():
    result = format_pending_orders([])

    assert "없습니다" in result


def test_format_pending_orders_includes_fields():
    orders = [
        Order(
            order_id="O001",
            sample_id="S001",
            customer_name="고객A",
            quantity=10,
            status=OrderStatus.RESERVED,
            created_at="2026-07-15T10:00:00",
        )
    ]

    result = format_pending_orders(orders)

    assert "O001" in result
    assert "S001" in result
    assert "고객A" in result
    assert "10" in result
    assert "RESERVED" in result


def test_format_pending_orders_header_columns_are_separated():
    orders = [
        Order(
            order_id="O001",
            sample_id="S001",
            customer_name="고객A",
            quantity=10,
            status=OrderStatus.RESERVED,
            created_at="2026-07-15T10:00:00",
        )
    ]

    header_line = format_pending_orders(orders).splitlines()[0]

    # "주문ID"와 "시료ID" 사이에 공백이 있어야 함 (컬럼이 서로 붙어있지 않음)
    assert "주문ID  " in header_line


def test_format_stock_check_includes_quantities():
    check = StockCheck(
        order_id="O001", sample_id="S001", quantity=10, inventory_quantity=4, shortfall=6
    )

    result = format_stock_check(check)

    assert "4" in result
    assert "10" in result
    assert "6" in result
