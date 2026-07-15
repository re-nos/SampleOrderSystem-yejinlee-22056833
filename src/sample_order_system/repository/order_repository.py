from sample_order_system.models.order import Order
from sample_order_system.repository.json_repository import JsonRepository


class OrderRepository(JsonRepository[Order]):
    def __init__(self, file_path: str = "data/order.json"):
        super().__init__(file_path=file_path, entity_type=Order, id_field="order_id")
