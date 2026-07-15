from dataclasses import dataclass


@dataclass
class ProductionJobDetail:
    """생산 라인 화면 표시를 위한, 생산 큐 항목 + 주문/시료 정보 결합 조회 전용 모델."""

    order_id: str
    sample_id: str
    sample_name: str
    order_quantity: int
    inventory_at_approval: int
    shortfall: int
    actual_production_qty: int
    yield_rate: float
    total_production_turns: int
    remaining_turns: int
