from sample_order_system.models.production_job_detail import ProductionJobDetail


def test_production_job_detail_fields():
    detail = ProductionJobDetail(
        order_id="O001",
        sample_id="S001",
        sample_name="시료A",
        order_quantity=10,
        inventory_at_approval=4,
        shortfall=6,
        actual_production_qty=15,
        yield_rate=0.4,
        total_production_turns=45,
        remaining_turns=30,
    )

    assert detail.order_id == "O001"
    assert detail.sample_name == "시료A"
    assert detail.inventory_at_approval == 4
    assert detail.remaining_turns == 30
