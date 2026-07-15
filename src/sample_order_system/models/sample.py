from dataclasses import dataclass


@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float


@dataclass
class SampleSummary:
    """시료 정보와 현재 재고를 함께 표현하는 조회 전용 모델."""

    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float
    quantity: int
