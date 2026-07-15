from typing import List, Optional

from sample_order_system.models.order import Order
from sample_order_system.models.production_queue import ProductionQueueEntry


def format_current_job(job: Optional[ProductionQueueEntry]) -> str:
    if job is None:
        return "현재 진행 중인 생산 작업이 없습니다."
    return (
        f"[진행 중] 주문 {job.order_id} (시료 {job.sample_id}) "
        f"남은 턴: {job.remaining_turns}/{job.total_production_turns}"
    )


def format_waiting_jobs(jobs: List[ProductionQueueEntry]) -> str:
    if not jobs:
        return "대기 중인 생산 작업이 없습니다."
    lines = [f"주문 {job.order_id} (시료 {job.sample_id}, 대기)" for job in jobs]
    return "\n".join(lines)


def format_turn_advance_result(completed_orders: List[Order]) -> str:
    if not completed_orders:
        return "이번 턴에 완료된 생산 작업이 없습니다."
    lines = [f"주문 {order.order_id} 생산 완료 → {order.status.value}" for order in completed_orders]
    return "\n".join(lines)
