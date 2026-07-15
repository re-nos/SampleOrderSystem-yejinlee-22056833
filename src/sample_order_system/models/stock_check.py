from dataclasses import dataclass


@dataclass
class StockCheck:
    """승인 전, 특정 주문에 대한 재고/부족분 확인 결과."""

    order_id: str
    sample_id: str
    quantity: int
    inventory_quantity: int
    shortfall: int
    actual_production_qty: int
    total_production_turns: int
