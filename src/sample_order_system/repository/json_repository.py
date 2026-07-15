import dataclasses
from enum import Enum
from typing import Generic, List, Type, TypeVar

from sample_order_system.common.exceptions import NotFoundError, ValidationError
from sample_order_system.repository.base import Repository
from sample_order_system.storage.json_file_storage import read_json, write_json

T = TypeVar("T")


class JsonRepository(Repository[T], Generic[T]):
    """JSON 파일을 저장소로 사용하는 범용 Repository 구현.

    dataclass 엔티티의 필드를 순회하며 직렬화/역직렬화하므로, 도메인별 하위
    클래스는 file_path/entity_type/id_field만 지정하면 된다.
    """

    def __init__(self, file_path: str, entity_type: Type[T], id_field: str):
        self._file_path = file_path
        self._entity_type = entity_type
        self._id_field = id_field

    def add(self, entity: T) -> T:
        records = self._load()
        entity_id = getattr(entity, self._id_field)

        if any(r[self._id_field] == entity_id for r in records):
            raise ValidationError(f"이미 존재하는 ID입니다: {entity_id}")

        records.append(self._to_record(entity))
        self._save(records)
        return entity

    def get(self, entity_id: str) -> T:
        for record in self._load():
            if record[self._id_field] == entity_id:
                return self._to_entity(record)
        raise NotFoundError(f"존재하지 않는 ID입니다: {entity_id}")

    def list(self) -> List[T]:
        return [self._to_entity(record) for record in self._load()]

    def update(self, entity: T) -> T:
        entity_id = getattr(entity, self._id_field)
        records = self._load()

        for i, record in enumerate(records):
            if record[self._id_field] == entity_id:
                records[i] = self._to_record(entity)
                self._save(records)
                return entity

        raise NotFoundError(f"존재하지 않는 ID입니다: {entity_id}")

    def delete(self, entity_id: str) -> None:
        records = self._load()
        remaining = [r for r in records if r[self._id_field] != entity_id]

        if len(remaining) == len(records):
            raise NotFoundError(f"존재하지 않는 ID입니다: {entity_id}")

        self._save(remaining)

    def _load(self) -> List[dict]:
        return read_json(self._file_path)

    def _save(self, records: List[dict]) -> None:
        write_json(self._file_path, records)

    def _to_record(self, entity: T) -> dict:
        record = {}
        for field in dataclasses.fields(entity):
            value = getattr(entity, field.name)
            if isinstance(value, Enum):
                value = value.value
            record[field.name] = value
        return record

    def _to_entity(self, record: dict) -> T:
        kwargs = {}
        for field in dataclasses.fields(self._entity_type):
            value = record[field.name]
            if isinstance(field.type, type) and issubclass(field.type, Enum):
                value = field.type(value)
            kwargs[field.name] = value
        return self._entity_type(**kwargs)
