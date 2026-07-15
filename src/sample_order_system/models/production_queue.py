from dataclasses import dataclass


@dataclass
class ProductionQueueEntry:
    order_id: str
    sample_id: str
    shortfall: int
    actual_production_qty: int
    total_production_turns: int
    remaining_turns: int
