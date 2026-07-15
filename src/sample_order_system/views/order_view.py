from sample_order_system.models.order import Order
from sample_order_system.views import colors


def format_order_registration_success(order: Order) -> str:
    status_cell = colors.colorize(order.status.value, colors.order_status_color(order.status.value))
    prefix = colors.colorize(f"주문 접수 완료: {order.order_id}", colors.SUCCESS)
    return (
        f"{prefix} (시료: {order.sample_id}, "
        f"고객: {order.customer_name}, 수량: {order.quantity}, 상태: {status_cell})"
    )
