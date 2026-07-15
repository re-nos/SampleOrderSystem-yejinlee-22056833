import os

import pytest

from sample_order_system.common.exceptions import ValidationError
from sample_order_system.controllers.sample_controller import SampleController
from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.sample import Sample, SampleSummary
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.sample_repository import SampleRepository


@pytest.fixture
def controller(tmp_path):
    sample_repo = SampleRepository(file_path=os.path.join(tmp_path, "sample.json"))
    inventory_repo = InventoryRepository(file_path=os.path.join(tmp_path, "inventory.json"))
    return SampleController(sample_repo=sample_repo, inventory_repo=inventory_repo)


def test_register_sample_returns_sample_and_initializes_zero_stock(controller):
    sample = controller.register_sample(
        sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8
    )

    assert sample == Sample(
        sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8
    )
    assert controller.list_samples() == [
        SampleSummary(
            sample_id="S001",
            name="시료A",
            avg_production_time=3.5,
            yield_rate=0.8,
            quantity=0,
        )
    ]


def test_register_sample_duplicate_id_raises_validation_error(controller):
    controller.register_sample(
        sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8
    )

    with pytest.raises(ValidationError):
        controller.register_sample(
            sample_id="S001", name="시료A-중복", avg_production_time=1.0, yield_rate=0.5
        )


def test_list_samples_reflects_updated_inventory_quantity(controller):
    controller.register_sample(
        sample_id="S001", name="시료A", avg_production_time=3.5, yield_rate=0.8
    )
    controller._inventory_repo.update(InventoryRecord(sample_id="S001", quantity=7))

    result = controller.list_samples()

    assert result[0].quantity == 7


def test_search_by_name_returns_matching_samples_with_quantity(controller):
    controller.register_sample(
        sample_id="S001", name="Wafer Alpha", avg_production_time=3.5, yield_rate=0.8
    )
    controller.register_sample(
        sample_id="S002", name="시료B", avg_production_time=2.0, yield_rate=0.9
    )

    result = controller.search_by_name("alpha")

    assert [s.sample_id for s in result] == ["S001"]
    assert result[0].quantity == 0


def test_search_by_name_no_match_returns_empty_list(controller):
    controller.register_sample(
        sample_id="S001", name="Wafer Alpha", avg_production_time=3.5, yield_rate=0.8
    )

    assert controller.search_by_name("없는이름") == []
