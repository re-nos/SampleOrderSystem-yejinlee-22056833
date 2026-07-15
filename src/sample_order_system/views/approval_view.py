from sample_order_system.models.order import Order
from sample_order_system.views import colors


def format_approval_result(order: Order) -> str:
    status_cell = colors.colorize(order.status.value, colors.order_status_color(order.status.value))
    return f"주문 {order.order_id} 처리 결과: {status_cell}"
