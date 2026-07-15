from typing import List

from sample_order_system.models.inventory import InventoryRecord
from sample_order_system.models.sample import Sample, SampleSummary
from sample_order_system.repository.inventory_repository import InventoryRepository
from sample_order_system.repository.sample_repository import SampleRepository


class SampleController:
    """시료 등록, 목록 조회, 이름 검색 유스케이스를 담당."""

    def __init__(self, sample_repo: SampleRepository, inventory_repo: InventoryRepository) -> None:
        self._sample_repo = sample_repo
        self._inventory_repo = inventory_repo

    def register_sample(
        self, sample_id: str, name: str, avg_production_time: float, yield_rate: float
    ) -> Sample:
        sample = Sample(
            sample_id=sample_id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
        )
        self._sample_repo.add(sample)
        self._inventory_repo.add(InventoryRecord(sample_id=sample_id, quantity=0))
        return sample

    def list_samples(self) -> List[SampleSummary]:
        return [self._to_summary(sample) for sample in self._sample_repo.list()]

    def search_by_name(self, keyword: str) -> List[SampleSummary]:
        return [self._to_summary(sample) for sample in self._sample_repo.search_by_name(keyword)]

    def _to_summary(self, sample: Sample) -> SampleSummary:
        inventory = self._inventory_repo.get(sample.sample_id)
        return SampleSummary(
            sample_id=sample.sample_id,
            name=sample.name,
            avg_production_time=sample.avg_production_time,
            yield_rate=sample.yield_rate,
            quantity=inventory.quantity,
        )
