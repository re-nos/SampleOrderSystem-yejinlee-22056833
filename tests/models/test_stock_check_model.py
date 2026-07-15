from sample_order_system.models.stock_check import StockCheck


def test_stock_check_fields():
    check = StockCheck(
        order_id="O001", sample_id="S001", quantity=10, inventory_quantity=4, shortfall=6
    )

    assert check.order_id == "O001"
    assert check.quantity == 10
    assert check.inventory_quantity == 4
    assert check.shortfall == 6
