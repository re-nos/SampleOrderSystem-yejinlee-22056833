# Phase 4. 모니터링 — 상세 계획

`PLAN.md`의 Phase 4 항목을 구체화한 문서입니다. 이 계획을 승인받은 뒤 구현을 시작합니다.

## 1. PoC 리뷰 요약 및 설계 결정

- `ConsoleMVC`의 `MonitoringController.count_by_status()`: `RESERVED`/`PRODUCING`/`CONFIRMED`/`RELEASE` 4개 상태만 집계(`REJECTED` 제외), 주문이 없는 상태도 0으로 표시
- 재고 상태/잔여율 판정 방식은 `ConsoleMVC`(미결 주문 수요 대비)와 `DataMonitor`(기준재고 대비)가 서로 달라 사용자 확인 결과 **미결 주문 수요 대비 방식(ConsoleMVC)**으로 확정:
  - `demand`(해당 시료의 `RESERVED` 상태 주문 수량 합계) 대비 현재 재고 비율로 판정
  - 재고 0 → `고갈`, `잔여율 0%`
  - `demand == 0`(수요 없음) → `여유`, `잔여율 100%`
  - 그 외: `잔여율 = min(재고/demand * 100, 100)`, `재고 >= demand`면 `여유`, 아니면 `부족`
  - 이 방식은 기존 스키마(Sample/Order/Inventory)만으로 계산 가능하며 신규 필드가 필요 없음

## 2. Phase 0~3 대비 변경 사항

- 없음 (신규 모델 `StockStatus`는 조회 전용 DTO로 기존 엔티티에 필드 추가 없이 별도 정의)

## 3. 신규 파일

```
src/sample_order_system/
├── models/
│   └── monitoring.py           # (신규) StockStatus DTO
├── controllers/
│   └── monitoring_controller.py  # (신규) count_by_status, stock_status
├── views/
│   └── monitoring_view.py       # (신규) 순수 포맷팅 함수
tests/
├── controllers/test_monitoring_controller.py
└── views/test_monitoring_view.py
```

## 4. 설계 상세

### `StockStatus` (`models/monitoring.py`)
```python
@dataclass
class StockStatus:
    sample_id: str
    name: str
    quantity: int
    status: str            # "여유" | "부족" | "고갈"
    remaining_ratio: float  # 0.0 ~ 100.0
```

### `MonitoringController`
- `__init__(self, sample_repo, inventory_repo, order_repo)`
- `count_by_status() -> dict[str, int]`
  - `{"RESERVED": 0, "PRODUCING": 0, "CONFIRMED": 0, "RELEASE": 0}`로 초기화 후 `order_repo.list()`를 순회하며 증가 (`REJECTED`는 무시, 딕셔너리에 키 자체가 없음)
- `stock_status() -> list[StockStatus]`
  - 등록된 모든 시료에 대해 재고(`inventory_repo.get`)와 수요(`order_repo.list()`에서 해당 `sample_id`, `status == RESERVED`인 주문의 `quantity` 합)를 계산해 위 판정 규칙 적용

### `views/monitoring_view.py`
- `format_order_counts(counts: dict) -> str`
- `format_stock_status_list(statuses: list[StockStatus]) -> str` (빈 리스트면 안내 문구)

## 5. TDD 테스트 케이스

**`MonitoringController`**
- `count_by_status`: `REJECTED` 제외 확인, 각 상태별 정확한 건수, 주문이 하나도 없을 때 전부 0
- `stock_status`:
  - 재고 0 → `고갈`, 잔여율 0 (수요 유무 무관)
  - 수요 없음(재고>0, RESERVED 주문 없음) → `여유`, 잔여율 100
  - 수요가 재고 초과 → `부족`, 잔여율 = 재고/수요*100
  - 재고가 수요를 충족(재고 ≥ 수요) → `여유`, 잔여율 100(캡)
  - 시료 여러 개 등록 시 각각에 대해 하나씩 반환

**`monitoring_view`**
- `format_order_counts`: 각 상태와 건수가 출력에 포함
- `format_stock_status_list`: 빈 리스트 안내 문구, 항목 있을 때 필드 포함 여부

## 6. 완료 기준

- 위 테스트가 모두 통과
- 전체 `pytest` 통과 (Phase 0~3 회귀 포함)
- `reports/phase4.md` 작성 후 사용자 확인
