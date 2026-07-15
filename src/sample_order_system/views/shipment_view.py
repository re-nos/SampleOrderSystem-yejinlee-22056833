from sample_order_system.models.order import Order


def format_release_result(order: Order) -> str:
    return f"주문 {order.order_id} 출고 완료: {order.status.value}"
