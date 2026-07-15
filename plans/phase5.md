# Phase 5. 출고 처리 — 상세 계획

`PLAN.md`의 Phase 5 항목을 구체화한 문서입니다. 이 계획을 승인받은 뒤 구현을 시작합니다.

## 1. PoC 리뷰 요약 (`ConsoleMVC-yejinlee-22056833`)

- `controllers/shipment_controller.py`의 `release(order_id)`: 주문 조회 → `CONFIRMED` 상태가 아니면 예외 → `RELEASE`로 전환. 다른 Phase의 승인/거절 컨트롤러와 동일한 상태 검증 패턴(`InvalidStateError`/본 프로젝트의 `InvalidStateTransitionError`)을 그대로 따름
- 테스트 케이스(정상 출고/미확인 주문/생산 중 주문/중복 출고)가 그대로 본 프로젝트에도 적용 가능한 범위

## 2. Phase 0~4 대비 변경 사항

- 없음. 기존 `Order`, `OrderRepository`, `InvalidStateTransitionError`만 사용

## 3. 신규 파일

```
src/sample_order_system/
├── controllers/
│   └── shipment_controller.py   # (신규) 출고 처리 유스케이스
├── views/
│   └── shipment_view.py         # (신규) 순수 포맷팅 함수
tests/
├── controllers/test_shipment_controller.py
└── views/test_shipment_view.py
```

## 4. 설계 상세

### `ShipmentController`
- `__init__(self, order_repo: OrderRepository)`
- `release(order_id: str) -> Order`
  1. `order = order_repo.get(order_id)`
  2. `status != CONFIRMED`면 `InvalidStateTransitionError`
  3. `order.status = RELEASE` 후 `order_repo.update(order)`, 반환

### `views/shipment_view.py`
- `format_release_result(order: Order) -> str`: 주문ID/상태 포함

## 5. TDD 테스트 케이스

**`ShipmentController`**
- `CONFIRMED` 주문 출고 → `RELEASE` 전환
- `RESERVED` 주문 출고 시도 → `InvalidStateTransitionError`
- `PRODUCING` 주문 출고 시도 → `InvalidStateTransitionError`
- 이미 `RELEASE`된 주문 재출고 시도 → `InvalidStateTransitionError` (중복 출고 방지)

**`shipment_view`**
- `format_release_result`: 주문ID/상태가 출력 문자열에 포함되는지 검증

## 6. 완료 기준

- 위 테스트가 모두 통과
- 전체 `pytest` 통과 (Phase 0~4 회귀 포함)
- `reports/phase5.md` 작성 후 사용자 확인
