from typing import List

from sample_order_system.models.order import Order
from sample_order_system.models.stock_check import StockCheck
from sample_order_system.views import colors
from sample_order_system.views.text_width import pad

_SEPARATOR = "-" * 71

_COLS = {"num": 6, "id": 14, "customer": 18, "sample_id": 10, "quantity": 8, "status": 12}


def format_approval_result(order: Order) -> str:
    status_cell = colors.colorize(order.status.value, colors.order_status_color(order.status.value))
    return f"주문 {order.order_id} 처리 결과: {status_cell}"


def format_pending_orders(orders: List[Order]) -> str:
    if not orders:
        return "승인 대기 중인 주문이 없습니다."

    header = (
        pad("번호", _COLS["num"])
        + pad("주문번호", _COLS["id"])
        + pad("고객", _COLS["customer"])
        + pad("시료ID", _COLS["sample_id"])
        + pad("수량", _COLS["quantity"])
        + pad("상태", _COLS["status"])
    )
    lines = [
        colors.colorize("승인 대기 중인 예약 목록 (RESERVED)", colors.HEADER),
        colors.colorize(header, colors.HEADER),
        colors.colorize(_SEPARATOR, colors.SEPARATOR),
    ]

    for i, o in enumerate(orders, start=1):
        status_cell = colors.colorize(
            pad(o.status.value, _COLS["status"]), colors.order_status_color(o.status.value)
        )
        row = (
            pad(f"[{i}]", _COLS["num"])
            + pad(o.order_id, _COLS["id"])
            + pad(o.customer_name, _COLS["customer"])
            + pad(o.sample_id, _COLS["sample_id"])
            + pad(f"{o.quantity} ea", _COLS["quantity"])
            + status_cell
        )
        lines.append(row)
    return "\n".join(lines)


def format_stock_check(check: StockCheck) -> str:
    lines = [
        f"시료      {check.sample_id}   주문 수량  {check.quantity} ea",
        f"현재 재고 {check.inventory_quantity} ea",
    ]

    if check.shortfall > 0:
        lines.append(f"부족분    {check.shortfall} ea  ← 이 수량만 생산")
        lines.append("")
        lines.append(
            f"재고 부족, 부족분 {check.shortfall} ea 승인하시겠습니까? "
            f"(실생산량 {check.actual_production_qty} ea / {check.total_production_turns} min)"
        )
    else:
        lines.append("")
        lines.append("재고 충분, 즉시 승인하시겠습니까?")

    return "\n".join(lines)
