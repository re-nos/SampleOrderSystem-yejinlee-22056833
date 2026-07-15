from typing import Dict, List

from sample_order_system.models.monitoring import StockStatus
from sample_order_system.views import colors
from sample_order_system.views.text_width import pad

_SEPARATOR = "-" * 71

_STOCK_COLS = {"id": 8, "name": 16, "quantity": 8, "status": 8}


def format_order_counts(counts: Dict[str, int]) -> str:
    lines = [colors.colorize("[주문 상태별 건수]", colors.HEADER)]
    for status, count in counts.items():
        status_cell = colors.colorize(pad(status, 12), colors.order_status_color(status))
        lines.append(f"  {status_cell}: {count}건")
    return "\n".join(lines)


def format_stock_status_list(statuses: List[StockStatus]) -> str:
    if not statuses:
        return "등록된 시료가 없습니다."

    header = (
        pad("시료ID", _STOCK_COLS["id"])
        + pad("이름", _STOCK_COLS["name"])
        + pad("재고", _STOCK_COLS["quantity"])
        + pad("상태", _STOCK_COLS["status"])
        + "잔여율"
    )
    lines = [colors.colorize(header, colors.HEADER), colors.colorize(_SEPARATOR, colors.SEPARATOR)]

    for s in statuses:
        status_cell = colors.colorize(
            pad(s.status, _STOCK_COLS["status"]), colors.stock_status_color(s.status)
        )
        row = (
            pad(s.sample_id, _STOCK_COLS["id"])
            + pad(s.name, _STOCK_COLS["name"])
            + pad(str(s.quantity), _STOCK_COLS["quantity"])
            + status_cell
            + f"{s.remaining_ratio:.1f}%"
        )
        lines.append(row)
    return "\n".join(lines)
