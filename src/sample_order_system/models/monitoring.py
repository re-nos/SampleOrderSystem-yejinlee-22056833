from dataclasses import dataclass


@dataclass
class StockStatus:
    """시료별 재고 상태(여유/부족/고갈)와 잔여율을 표현하는 조회 전용 모델."""

    sample_id: str
    name: str
    quantity: int
    status: str
    remaining_ratio: float
