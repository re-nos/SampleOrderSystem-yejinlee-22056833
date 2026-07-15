from sample_order_system.models.order import Order


def format_order_registration_success(order: Order) -> str:
    return (
        f"주문 접수 완료: {order.order_id} (시료: {order.sample_id}, "
        f"고객: {order.customer_name}, 수량: {order.quantity}, 상태: {order.status.value})"
    )
