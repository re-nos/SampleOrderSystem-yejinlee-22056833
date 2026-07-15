from typing import List

from sample_order_system.common.exceptions import InvalidStateTransitionError
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.repository.order_repository import OrderRepository


class ShipmentController:
    """CONFIRMED 상태 주문의 출고(RELEASE) 처리를 담당."""

    def __init__(self, order_repo: OrderRepository) -> None:
        self._order_repo = order_repo

    def list_releasable_orders(self) -> List[Order]:
        return [o for o in self._order_repo.list() if o.status == OrderStatus.CONFIRMED]

    def release(self, order_id: str) -> Order:
        order = self._order_repo.get(order_id)
        if order.status != OrderStatus.CONFIRMED:
            raise InvalidStateTransitionError(
                f"CONFIRMED 상태의 주문만 출고할 수 있습니다: {order_id}"
            )

        order.status = OrderStatus.RELEASE
        return self._order_repo.update(order)
