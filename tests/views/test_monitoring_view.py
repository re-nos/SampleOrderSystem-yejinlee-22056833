from sample_order_system.models.monitoring import StockStatus
from sample_order_system.views.monitoring_view import (
    format_order_counts,
    format_stock_status_list,
)


def test_format_order_counts_includes_each_status_and_count():
    counts = {"RESERVED": 1, "PRODUCING": 2, "CONFIRMED": 0, "RELEASE": 3}

    result = format_order_counts(counts)

    assert "RESERVED" in result
    assert "1" in result
    assert "PRODUCING" in result
    assert "2" in result


def test_format_stock_status_list_empty_shows_guidance_message():
    result = format_stock_status_list([])

    assert "없습니다" in result


def test_format_stock_status_list_includes_fields():
    statuses = [
        StockStatus(sample_id="S001", name="시료A", quantity=4, status="부족", remaining_ratio=40.0)
    ]

    result = format_stock_status_list(statuses)

    assert "S001" in result
    assert "시료A" in result
    assert "부족" in result
    assert "40.0" in result
