from typing import List, Optional

from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.production_queue import ProductionQueueEntry
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.production_queue_repository import (
    ProductionQueueRepository,
)


class ProductionController:
    """생산 라인의 턴 진행 및 현재/대기 작업 조회를 담당."""

    def __init__(
        self,
        order_repo: OrderRepository,
        inventory_repo: InventoryRepository,
        production_queue_repo: ProductionQueueRepository,
    ) -> None:
        self._order_repo = order_repo
        self._inventory_repo = inventory_repo
        self._production_queue_repo = production_queue_repo

    def advance_turns(self, turns: int) -> List[Order]:
        completed_orders: List[Order] = []
        remaining = turns

        while remaining > 0:
            queue = self._production_queue_repo.list()
            if not queue:
                break

            job = queue[0]
            consumed = min(remaining, job.remaining_turns)
            job.remaining_turns -= consumed
            remaining -= consumed

            if job.remaining_turns <= 0:
                completed_orders.append(self._complete_job(job))
            else:
                self._production_queue_repo.update(job)
                break

        return completed_orders

    def current_job(self) -> Optional[ProductionQueueEntry]:
        queue = self._production_queue_repo.list()
        return queue[0] if queue else None

    def waiting_jobs(self) -> List[ProductionQueueEntry]:
        return self._production_queue_repo.list()[1:]

    def _complete_job(self, job: ProductionQueueEntry) -> Order:
        leftover = job.actual_production_qty - job.shortfall
        inventory = self._inventory_repo.get(job.sample_id)
        self._inventory_repo.update(
            InventoryRecord(sample_id=job.sample_id, quantity=inventory.quantity + leftover)
        )

        order = self._order_repo.get(job.order_id)
        order.status = OrderStatus.CONFIRMED
        self._order_repo.update(order)

        self._production_queue_repo.delete(job.order_id)
        return order
