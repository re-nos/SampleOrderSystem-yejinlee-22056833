from dataclasses import dataclass


@dataclass
class InventoryRecord:
    sample_id: str
    quantity: int
