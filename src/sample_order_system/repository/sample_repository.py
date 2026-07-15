from sample_order_system.models.sample import Sample
from sample_order_system.repository.json_repository import JsonRepository


class SampleRepository(JsonRepository[Sample]):
    def __init__(self, file_path: str = "data/sample.json"):
        super().__init__(file_path=file_path, entity_type=Sample, id_field="sample_id")
