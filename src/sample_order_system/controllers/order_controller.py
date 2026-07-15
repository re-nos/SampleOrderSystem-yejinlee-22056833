from datetime import datetime
from typing import Callable

from sample_order_system.common.exceptions import ValidationError
from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.repository.order_repository import OrderRepository
from sample_order_system.repository.sample_repository import SampleRepository


class OrderController:
    """고객 주문 접수(RESERVED) 유스케이스를 담당."""

    def __init__(
        self,
        sample_repo: SampleRepository,
        order_repo: OrderRepository,
        clock: Callable[[], str] = lambda: datetime.now().isoformat(),
    ) -> None:
        self._sample_repo = sample_repo
        self._order_repo = order_repo
        self._clock = clock

    def place_order(self, sample_id: str, customer_name: str, quantity: int) -> Order:
        if quantity <= 0:
            raise ValidationError("주문 수량은 1 이상이어야 합니다.")

        self._sample_repo.get(sample_id)  # 존재하지 않으면 NotFoundError 발생

        order = Order(
            order_id=self._next_order_id(),
            sample_id=sample_id,
            customer_name=customer_name,
            quantity=quantity,
            status=OrderStatus.RESERVED,
            created_at=self._clock(),
        )
        return self._order_repo.add(order)

    def _next_order_id(self) -> str:
        date_part = self._clock()[:10].replace("-", "")
        seq = len(self._order_repo.list()) + 1
        return f"ORD-{date_part}-{seq:04d}"
