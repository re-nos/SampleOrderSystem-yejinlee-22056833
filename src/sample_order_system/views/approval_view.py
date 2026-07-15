from typing import List

from sample_order_system.models.order import Order
from sample_order_system.models.stock_check import StockCheck
from sample_order_system.views import colors
from sample_order_system.views.text_width import pad

_SEPARATOR = "-" * 71

_COLS = {"id": 6, "sample_id": 8, "customer": 18, "quantity": 8, "status": 12}


def format_approval_result(order: Order) -> str:
    status_cell = colors.colorize(order.status.value, colors.order_status_color(order.status.value))
    return f"주문 {order.order_id} 처리 결과: {status_cell}"


def format_pending_orders(orders: List[Order]) -> str:
    if not orders:
        return "승인 대기 중인 주문이 없습니다."

    header = (
        pad("주문ID", _COLS["id"])
        + pad("시료ID", _COLS["sample_id"])
        + pad("고객명", _COLS["customer"])
        + pad("수량", _COLS["quantity"])
        + pad("상태", _COLS["status"])
    )
    lines = [colors.colorize(header, colors.HEADER), colors.colorize(_SEPARATOR, colors.SEPARATOR)]

    for o in orders:
        status_cell = colors.colorize(
            pad(o.status.value, _COLS["status"]), colors.order_status_color(o.status.value)
        )
        row = (
            pad(o.order_id, _COLS["id"])
            + pad(o.sample_id, _COLS["sample_id"])
            + pad(o.customer_name, _COLS["customer"])
            + pad(str(o.quantity), _COLS["quantity"])
            + status_cell
        )
        lines.append(row)
    return "\n".join(lines)


def format_stock_check(check: StockCheck) -> str:
    return (
        f"[재고 확인] 시료 {check.sample_id} — 재고: {check.inventory_quantity} | "
        f"주문 수량: {check.quantity} | 부족분: {check.shortfall}"
    )
