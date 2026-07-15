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


def test_format_pending_orders_numbers_each_row():
    orders = [
        Order(
            order_id="O001",
            sample_id="S001",
            customer_name="고객A",
            quantity=10,
            status=OrderStatus.RESERVED,
            created_at="2026-07-15T10:00:00",
        ),
        Order(
            order_id="O002",
            sample_id="S001",
            customer_name="고객B",
            quantity=5,
            status=OrderStatus.RESERVED,
            created_at="2026-07-15T10:00:00",
        ),
    ]

    result = format_pending_orders(orders)

    assert "[1]" in result
    assert "[2]" in result


def test_format_pending_orders_long_order_id_does_not_collide_with_next_column():
    orders = [
        Order(
            order_id="ORD-20260715-0001",
            sample_id="S001",
            customer_name="고객A",
            quantity=10,
            status=OrderStatus.RESERVED,
            created_at="2026-07-15T10:00:00",
        )
    ]

    data_line = format_pending_orders(orders).splitlines()[3]

    assert "ORD-20260715-0001 " in data_line  # 주문번호 뒤에 공백이 있어야 함(컬럼 붙음 방지)


def test_format_stock_check_shows_shortfall_and_production_estimate():
    check = StockCheck(
        order_id="O001",
        sample_id="S001",
        quantity=10,
        inventory_quantity=4,
        shortfall=6,
        actual_production_qty=15,
        total_production_turns=45,
    )

    result = format_stock_check(check)

    assert "4" in result
    assert "10" in result
    assert "6" in result
    assert "15" in result
    assert "45" in result
    assert "부족" in result


def test_format_stock_check_sufficient_stock_message():
    check = StockCheck(
        order_id="O001",
        sample_id="S001",
        quantity=10,
        inventory_quantity=20,
        shortfall=0,
        actual_production_qty=0,
        total_production_turns=0,
    )

    result = format_stock_check(check)

    assert "충분" in result
