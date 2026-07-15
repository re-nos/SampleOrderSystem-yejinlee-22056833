# Phase 1. 시료 관리 — 상세 계획

`PLAN.md`의 Phase 1 항목을 구체화한 문서입니다. 이 계획을 승인받은 뒤 구현을 시작합니다.

## 1. PoC 리뷰 요약 (`ConsoleMVC-yejinlee-22056833`)

- `controllers/sample_controller.py`: `register_sample`, `list_samples`, `search_by_name` 3개 유스케이스만 얇게 구현, Repository에 위임
- `models/repository.py`의 `SampleRepository`: `add`(중복 ID 시 예외), `list_all`, `search_by_name`(대소문자 무시 부분일치) 제공
- `views/console_view.py`: `input()`을 직접 호출하는 `prompt_*` 함수와, 데이터만 받아 포맷팅/출력하는 `print_*` 함수를 명확히 분리 — 입출력 책임 분리 패턴을 그대로 채택
- PoC의 `Sample`은 `stock` 필드를 모델에 직접 포함하지만, 본 프로젝트는 Phase 0에서 이미 `InventoryRecord`를 별도 엔티티로 분리했으므로 이 구조를 유지 (재고는 생산 라인 완료 시 갱신되는 별개의 가변 상태이므로 분리가 더 적합)

## 2. Phase 0 대비 변경 사항

- `models/sample.py`의 `avg_production_time` 타입을 `int` → `float`로 변경 (생산 시간이 정수로 한정될 이유가 없고, PoC도 `float` 사용). 기존 Phase 0 테스트(`tests/models/test_models.py`)의 관련 값도 함께 갱신
- 그 외 Phase 0 산출물(예외, storage, JsonRepository)은 변경 없이 재사용

## 3. 신규/변경 파일

```
src/sample_order_system/
├── repository/
│   └── inventory_repository.py   # (신규) InventoryRecord용 Repository, id_field="sample_id"
├── controllers/
│   └── sample_controller.py      # (신규) 등록/조회/검색 유스케이스
├── views/
│   └── sample_view.py            # (신규) 순수 포맷팅 함수 (입력 없음)
tests/
├── repository/test_inventory_repository.py   # (신규)
├── controllers/test_sample_controller.py     # (신규)
└── views/test_sample_view.py                 # (신규)
```

`views/`는 이번 Phase에서 **순수 포맷팅 함수만** 구현합니다 (`input()` 직접 호출 없음). 실제 `input()`을 통한 콘솔 메뉴 루프는 모든 Controller가 갖춰지는 Phase 6(`app.py`)에서 통합합니다.

## 4. 설계 상세

### `InventoryRepository`
```python
class InventoryRepository(JsonRepository[InventoryRecord]):
    def __init__(self, file_path: str = "data/inventory.json"):
        super().__init__(file_path=file_path, entity_type=InventoryRecord, id_field="sample_id")
```

### `SampleController`
- `__init__(self, sample_repo: SampleRepository, inventory_repo: InventoryRepository)`
- `register_sample(sample_id, name, avg_production_time, yield_rate) -> Sample`
  - `SampleRepository.add()`로 등록 (중복 ID면 `ValidationError` — Phase 0에서 이미 구현됨)
  - 등록 성공 시 `InventoryRepository.add(InventoryRecord(sample_id, quantity=0))`으로 재고 0 초기화
- `list_samples() -> list[SampleSummary]`
- `search_by_name(keyword: str) -> list[SampleSummary]`
  - `SampleRepository`에 신규 메서드 `search_by_name(keyword)` 추가 (대소문자 무시 부분일치, PoC 패턴)
  - 결과 없으면 빈 리스트 반환 (예외 아님)
- 위 두 조회 메서드는 각 시료에 대응하는 재고 수량을 `InventoryRepository`에서 조회해 함께 반환

**`SampleSummary`** (신규, `models/sample.py`에 추가): 시료 정보 + 현재 재고를 함께 표현하는 조회 전용 dataclass
```python
@dataclass
class SampleSummary:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float
    quantity: int
```

### `views/sample_view.py`
- `format_sample_list(summaries: list[SampleSummary]) -> str`: 표 형태 문자열 반환 (빈 리스트면 안내 문구)
- `format_registration_success(sample: Sample) -> str`

## 5. TDD 테스트 케이스

- **`InventoryRepository`**: 기존 `JsonRepository` 제네릭 테스트로 커버되는 범위이므로, 파일 경로/엔티티 매핑만 검증하는 최소 테스트 1~2개
- **`SampleController`**
  - 정상 등록 시 `Sample` 반환 및 `InventoryRecord(quantity=0)` 함께 생성됨
  - 중복 ID 등록 시 `ValidationError`
  - `list_samples()`: 등록된 시료 + 재고 수량이 함께 반환됨 (재고가 생산 완료로 갱신된 경우도 반영되는지)
  - `search_by_name()`: 대소문자 무시 부분일치 정상 케이스, 일치 없음 → 빈 리스트
- **`sample_view`**
  - `format_sample_list`: 빈 리스트 입력 시 안내 문구, 항목 있을 때 각 필드가 출력 문자열에 포함되는지
  - `format_registration_success`: 등록된 시료 정보가 포함되는지

## 6. 완료 기준

- 위 테스트가 모두 통과
- 전체 `pytest` 통과 (Phase 0 회귀 포함)
- `reports/phase1.md` 작성 후 사용자 확인
