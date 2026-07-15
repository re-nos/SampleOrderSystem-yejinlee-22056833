from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.repository.json_repository import JsonRepository


class InventoryRepository(JsonRepository[InventoryRecord]):
    def __init__(self, file_path: str = "data/inventory.json"):
        super().__init__(file_path=file_path, entity_type=InventoryRecord, id_field="sample_id")
