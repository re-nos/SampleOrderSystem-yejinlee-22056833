from math import ceil

from sample_order_system.common.exceptions import InvalidStateTransitionError
from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.production_queue import ProductionQueueEntry
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.production_queue_repository import (
    ProductionQueueRepository,
)
from sample_order_system.repository.sample_repository import SampleRepository


class ApprovalController:
    """RESERVED 주문의 승인/거절 및 생산 라인 등록을 담당."""

    def __init__(
        self,
        sample_repo: SampleRepository,
        order_repo: OrderRepository,
        inventory_repo: InventoryRepository,
        production_queue_repo: ProductionQueueRepository,
    ) -> None:
        self._sample_repo = sample_repo
        self._order_repo = order_repo
        self._inventory_repo = inventory_repo
        self._production_queue_repo = production_queue_repo

    def approve(self, order_id: str) -> Order:
        order = self._require_reserved(order_id, action="승인")
        inventory = self._inventory_repo.get(order.sample_id)

        if inventory.quantity >= order.quantity:
            self._inventory_repo.update(
                InventoryRecord(
                    sample_id=order.sample_id, quantity=inventory.quantity - order.quantity
                )
            )
            order.status = OrderStatus.CONFIRMED
        else:
            shortfall = order.quantity - inventory.quantity
            self._inventory_repo.update(InventoryRecord(sample_id=order.sample_id, quantity=0))

            sample = self._sample_repo.get(order.sample_id)
            actual_production_qty = ceil(shortfall / sample.yield_rate)
            total_production_turns = ceil(sample.avg_production_time * actual_production_qty)

            self._production_queue_repo.add(
                ProductionQueueEntry(
                    order_id=order.order_id,
                    sample_id=order.sample_id,
                    shortfall=shortfall,
                    actual_production_qty=actual_production_qty,
                    total_production_turns=total_production_turns,
                    remaining_turns=total_production_turns,
                )
            )
            order.status = OrderStatus.PRODUCING

        return self._order_repo.update(order)

    def reject(self, order_id: str) -> Order:
        order = self._require_reserved(order_id, action="거절")
        order.status = OrderStatus.REJECTED
        return self._order_repo.update(order)

    def _require_reserved(self, order_id: str, action: str) -> Order:
        order = self._order_repo.get(order_id)
        if order.status != OrderStatus.RESERVED:
            raise InvalidStateTransitionError(
                f"RESERVED 상태의 주문만 {action}할 수 있습니다: {order_id}"
            )
        return order
