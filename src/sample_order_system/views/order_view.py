from sample_order_system.models.order import Order
from sample_order_system.models.sample import SampleSummary
from sample_order_system.views import colors


def format_order_confirmation(sample: SampleSummary, customer_name: str, quantity: int) -> str:
    return (
        f"입력 내용 확인\n"
        f"시료   {sample.name} ({sample.sample_id})\n"
        f"고객   {customer_name}\n"
        f"수량   {quantity} ea"
    )


def format_order_registration_success(order: Order) -> str:
    status_cell = colors.colorize(order.status.value, colors.order_status_color(order.status.value))
    prefix = colors.colorize("예약 접수 완료.", colors.SUCCESS)
    return f"{prefix}\n주문번호  {order.order_id}\n현재 상태 {status_cell}"


def format_order_cancelled() -> str:
    return colors.colorize("주문 접수가 취소되었습니다.", colors.ERROR)
