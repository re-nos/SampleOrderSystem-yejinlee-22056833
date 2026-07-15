from sample_order_system.models.production_queue import ProductionQueueEntry
from sample_order_system.repository.json_repository import JsonRepository


class ProductionQueueRepository(JsonRepository[ProductionQueueEntry]):
    def __init__(self, file_path: str = "data/production_queue.json"):
        super().__init__(
            file_path=file_path, entity_type=ProductionQueueEntry, id_field="order_id"
        )
