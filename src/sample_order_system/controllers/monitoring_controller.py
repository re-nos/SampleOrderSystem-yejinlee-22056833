from typing import Dict, List

from sample_order_system.models.monitoring import StockStatus
from sample_order_system.models.order import OrderStatus
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.sample_repository import SampleRepository

_MONITORED_STATUSES = (
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.CONFIRMED,
    OrderStatus.RELEASE,
)


class MonitoringController:
    """상태별 주문 건수 및 시료별 재고 현황 조회를 담당."""

    def __init__(
        self,
        sample_repo: SampleRepository,
        inventory_repo: InventoryRepository,
        order_repo: OrderRepository,
    ) -> None:
        self._sample_repo = sample_repo
        self._inventory_repo = inventory_repo
        self._order_repo = order_repo

    def count_by_status(self) -> Dict[str, int]:
        counts = {status.value: 0 for status in _MONITORED_STATUSES}
        for order in self._order_repo.list():
            if order.status in _MONITORED_STATUSES:
                counts[order.status.value] += 1
        return counts

    def stock_status(self) -> List[StockStatus]:
        orders = self._order_repo.list()
        return [self._build_stock_status(sample, orders) for sample in self._sample_repo.list()]

    def _build_stock_status(self, sample, orders) -> StockStatus:
        quantity = self._inventory_repo.get(sample.sample_id).quantity
        demand = sum(
            order.quantity
            for order in orders
            if order.sample_id == sample.sample_id and order.status == OrderStatus.RESERVED
        )

        if quantity == 0:
            status, ratio = "고갈", 0.0
        elif demand == 0:
            status, ratio = "여유", 100.0
        else:
            ratio = min(quantity / demand * 100, 100.0)
            status = "여유" if quantity >= demand else "부족"

        return StockStatus(
            sample_id=sample.sample_id,
            name=sample.name,
            quantity=quantity,
            status=status,
            remaining_ratio=ratio,
        )
