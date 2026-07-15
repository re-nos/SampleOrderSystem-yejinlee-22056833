from typing import List

from sample_order_system.models.order import Order
from sample_order_system.views import colors
from sample_order_system.views.text_width import pad

_SEPARATOR = "-" * 71

_COLS = {"num": 6, "id": 14, "customer": 14, "sample_id": 10, "quantity": 8}


def format_release_result(order: Order) -> str:
    status_cell = colors.colorize(order.status.value, colors.order_status_color(order.status.value))
    prefix = colors.colorize(f"주문 {order.order_id} 출고 완료:", colors.SUCCESS)
    return f"{prefix} {status_cell}"


def format_releasable_orders(orders: List[Order]) -> str:
    if not orders:
        return "출고 가능한 주문이 없습니다."

    header = (
        pad("번호", _COLS["num"])
        + pad("주문번호", _COLS["id"])
        + pad("고객", _COLS["customer"])
        + pad("시료ID", _COLS["sample_id"])
        + "수량"
    )
    lines = [
        colors.colorize("출고 가능 주문 (CONFIRMED)", colors.HEADER),
        colors.colorize(header, colors.HEADER),
        colors.colorize(_SEPARATOR, colors.SEPARATOR),
    ]

    for i, o in enumerate(orders, start=1):
        row = (
            pad(f"[{i}]", _COLS["num"])
            + pad(o.order_id, _COLS["id"])
            + pad(o.customer_name, _COLS["customer"])
            + pad(o.sample_id, _COLS["sample_id"])
            + f"{o.quantity} ea"
        )
        lines.append(row)
    return "\n".join(lines)
