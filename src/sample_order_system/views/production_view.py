from datetime import datetime, timedelta
from typing import List, Optional

from sample_order_system.models.order import Order
from sample_order_system.models.production_job_detail import ProductionJobDetail
from sample_order_system.views import colors
from sample_order_system.views.text_width import pad

_SEPARATOR = "-" * 71

_COLS = {"order": 6, "id": 20, "sample": 20, "qty": 10}


def format_current_job_detail(detail: Optional[ProductionJobDetail]) -> str:
    if detail is None:
        return "현재 진행 중인 생산 작업이 없습니다."

    total = detail.total_production_turns
    progress = round((total - detail.remaining_turns) / total * 100) if total else 100
    eta = (datetime.now() + timedelta(minutes=detail.remaining_turns)).strftime("%H:%M")

    lines = [
        colors.colorize("현재 처리 중", colors.HEADER),
        f"주문번호 {detail.order_id}",
        f"시료     {detail.sample_name}",
        f"{progress}% 진행 완료 예정 {eta}",
        (
            f"주문량 {detail.order_quantity} ea | 재고 {detail.inventory_at_approval} ea | "
            f"부족 {detail.shortfall} ea → 실생산량 {detail.actual_production_qty} ea "
            f"(수율 {detail.yield_rate} / {detail.total_production_turns} min)"
        ),
    ]
    return "\n".join(lines)


def format_waiting_job_details(
    details: List[ProductionJobDetail], current_remaining_turns: int = 0
) -> str:
    if not details:
        return "대기 중인 주문이 없습니다."

    header = (
        pad("순서", _COLS["order"])
        + pad("주문번호", _COLS["id"])
        + pad("시료", _COLS["sample"])
        + pad("주문량", _COLS["qty"])
        + pad("부족분", _COLS["qty"])
        + pad("실생산량", _COLS["qty"])
        + "예상 완료"
    )
    lines = [
        colors.colorize("대기 중인 주문 (FIFO 순)", colors.HEADER),
        colors.colorize(header, colors.HEADER),
        colors.colorize(_SEPARATOR, colors.SEPARATOR),
    ]

    cumulative_turns = current_remaining_turns
    for i, d in enumerate(details, start=1):
        cumulative_turns += d.total_production_turns
        eta = (datetime.now() + timedelta(minutes=cumulative_turns)).strftime("%H:%M")
        row = (
            pad(str(i), _COLS["order"])
            + pad(d.order_id, _COLS["id"])
            + pad(d.sample_name, _COLS["sample"])
            + pad(f"{d.order_quantity} ea", _COLS["qty"])
            + pad(f"{d.shortfall} ea", _COLS["qty"])
            + pad(f"{d.actual_production_qty} ea", _COLS["qty"])
            + eta
        )
        lines.append(row)

    lines.append("* 부족분 = 주문량 - 재고, 실생산량 = ceil(부족분/수율)")
    return "\n".join(lines)


def format_turn_advance_result(completed_orders: List[Order]) -> str:
    if not completed_orders:
        return "이번 턴에 완료된 생산 작업이 없습니다."
    lines = []
    for order in completed_orders:
        status_cell = colors.colorize(
            order.status.value, colors.order_status_color(order.status.value)
        )
        prefix = colors.colorize(f"주문 {order.order_id} 생산 완료 →", colors.SUCCESS)
        lines.append(f"{prefix} {status_cell}")
    return "\n".join(lines)
