from typing import Dict, List

from sample_order_system.models.monitoring import StockStatus
from sample_order_system.views import colors
from sample_order_system.views.text_width import pad

_SEPARATOR = "-" * 71

_STOCK_COLS = {"name": 20, "quantity": 10, "status": 8}

_DISPLAY_ORDER = ["RESERVED", "CONFIRMED", "PRODUCING", "RELEASE"]
_NOTES = {"PRODUCING": " - 생산라인 대기"}


def format_order_counts(counts: Dict[str, int]) -> str:
    lines = [colors.colorize("상태별 주문 현황", colors.HEADER)]
    for status in _DISPLAY_ORDER:
        if status not in counts:
            continue
        status_cell = colors.colorize(pad(status, 12), colors.order_status_color(status))
        note = _NOTES.get(status, "")
        lines.append(f"{status_cell} {counts[status]}건{note}")
    return "\n".join(lines)


def format_stock_status_list(statuses: List[StockStatus]) -> str:
    if not statuses:
        return "등록된 시료가 없습니다."

    header = (
        pad("시료명", _STOCK_COLS["name"])
        + pad("재고", _STOCK_COLS["quantity"])
        + pad("상태", _STOCK_COLS["status"])
        + "잔여율"
    )
    lines = [
        colors.colorize("재고 현황", colors.HEADER),
        colors.colorize(header, colors.HEADER),
        colors.colorize(_SEPARATOR, colors.SEPARATOR),
    ]

    for s in statuses:
        status_cell = colors.colorize(
            pad(s.status, _STOCK_COLS["status"]), colors.stock_status_color(s.status)
        )
        row = (
            pad(s.name, _STOCK_COLS["name"])
            + pad(f"{s.quantity} ea", _STOCK_COLS["quantity"])
            + status_cell
            + f"{round(s.remaining_ratio)}%"
        )
        lines.append(row)
    return "\n".join(lines)
