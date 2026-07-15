from sample_order_system.models.order import Order, OrderStatus
from sample_order_system.models.production_queue import ProductionQueueEntry
from sample_order_system.views.production_view import (
    format_current_job,
    format_turn_advance_result,
    format_waiting_jobs,
)


def test_format_current_job_none_shows_guidance_message():
    result = format_current_job(None)

    assert "없습니다" in result


def test_format_current_job_includes_fields():
    job = ProductionQueueEntry(
        order_id="O001", sample_id="S001", shortfall=10,
        actual_production_qty=25, total_production_turns=75, remaining_turns=30,
    )

    result = format_current_job(job)

    assert "O001" in result
    assert "S001" in result
    assert "30" in result


def test_format_waiting_jobs_empty_shows_guidance_message():
    result = format_waiting_jobs([])

    assert "없습니다" in result


def test_format_waiting_jobs_includes_each_job():
    jobs = [
        ProductionQueueEntry(
            order_id="O002", sample_id="S001", shortfall=5,
            actual_production_qty=10, total_production_turns=20, remaining_turns=20,
        )
    ]

    result = format_waiting_jobs(jobs)

    assert "O002" in result


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
