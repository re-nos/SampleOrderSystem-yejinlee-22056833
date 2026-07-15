from typing import Dict, List

from sample_order_system.models.monitoring import StockStatus


def format_order_counts(counts: Dict[str, int]) -> str:
    lines = [f"{status}: {count}건" for status, count in counts.items()]
    return "\n".join(lines)


def format_stock_status_list(statuses: List[StockStatus]) -> str:
    if not statuses:
        return "등록된 시료가 없습니다."

    lines = ["시료ID | 이름 | 재고 | 상태 | 잔여율"]
    for s in statuses:
        lines.append(
            f"{s.sample_id} | {s.name} | {s.quantity} | {s.status} | {s.remaining_ratio}"
        )
    return "\n".join(lines)
