from sample_order_system.models.monitoring import StockStatus


def test_stock_status_fields():
    status = StockStatus(
        sample_id="S001", name="시료A", quantity=4, status="부족", remaining_ratio=40.0
    )

    assert status.sample_id == "S001"
    assert status.status == "부족"
    assert status.remaining_ratio == 40.0
