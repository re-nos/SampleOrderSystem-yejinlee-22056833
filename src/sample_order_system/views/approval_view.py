from sample_order_system.models.order import Order


def format_approval_result(order: Order) -> str:
    return f"주문 {order.order_id} 처리 결과: {order.status.value}"
