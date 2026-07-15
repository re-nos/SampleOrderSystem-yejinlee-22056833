from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.production_job_detail import ProductionJobDetail
from sample_order_system.views.production_view import (
    format_current_job_detail,
    format_turn_advance_result,
    format_waiting_job_details,
)


def _detail(order_id="O001", remaining_turns=30, total_production_turns=75):
    return ProductionJobDetail(
        order_id=order_id,
        sample_id="S001",
        sample_name="시료A",
        order_quantity=10,
        inventory_at_approval=4,
        shortfall=6,
        actual_production_qty=15,
        yield_rate=0.4,
        total_production_turns=total_production_turns,
        remaining_turns=remaining_turns,
    )


def test_format_current_job_detail_none_shows_guidance_message():
    result = format_current_job_detail(None)

    assert "없습니다" in result


def test_format_current_job_detail_includes_progress_percentage():
    detail = _detail(remaining_turns=21, total_production_turns=75)  # 진행률 72%

    result = format_current_job_detail(detail)

    assert "O001" in result
    assert "시료A" in result
    assert "72%" in result
    assert "완료 예정" in result


def test_format_current_job_detail_includes_quantity_breakdown():
    detail = _detail()

    result = format_current_job_detail(detail)

    assert "10 ea" in result  # 주문량
    assert "4 ea" in result  # 재고
    assert "6 ea" in result  # 부족
    assert "15 ea" in result  # 실생산량
    assert "0.4" in result  # 수율


def test_format_waiting_job_details_empty_shows_guidance_message():
    result = format_waiting_job_details([])

    assert "없습니다" in result


def test_format_waiting_job_details_numbers_each_row_and_shows_eta():
    details = [_detail(order_id="O002", remaining_turns=10, total_production_turns=10)]

    result = format_waiting_job_details(details, current_remaining_turns=5)

    assert "1" in result
    assert "O002" in result
    assert "예상 완료" in result or "완료" in result


def test_format_waiting_job_details_long_order_id_does_not_collide_with_next_column():
    details = [
        _detail(order_id="ORD-20260715-0001", remaining_turns=10, total_production_turns=10)
    ]

    data_line = format_waiting_job_details(details, current_remaining_turns=5).splitlines()[3]

    assert "ORD-20260715-0001 " in data_line


def test_format_turn_advance_result_empty_shows_guidance_message():
    result = format_turn_advance_result([])

    assert "없습니다" in result


def test_format_turn_advance_result_includes_completed_orders():
    orders = [
        Order(
            order_id="O001",
            sample_id="S001",
            customer_name="고객A",
            quantity=10,
            status=OrderStatus.CONFIRMED,
            created_at="2026-07-15T10:00:00",
        )
    ]

    result = format_turn_advance_result(orders)

    assert "O001" in result
