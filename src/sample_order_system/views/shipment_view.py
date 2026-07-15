from sample_order_system.models.order import Order
from sample_order_system.views import colors


def format_release_result(order: Order) -> str:
    status_cell = colors.colorize(order.status.value, colors.order_status_color(order.status.value))
    prefix = colors.colorize(f"주문 {order.order_id} 출고 완료:", colors.SUCCESS)
    return f"{prefix} {status_cell}"
