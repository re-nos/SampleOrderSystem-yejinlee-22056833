# Phase 2. 시료 주문 접수 — 상세 계획

`PLAN.md`의 Phase 2 항목을 구체화한 문서입니다. 이 계획을 승인받은 뒤 구현을 시작합니다.

## 1. PoC 리뷰 요약 (`ConsoleMVC-yejinlee-22056833`)

- `controllers/order_controller.py`의 `place_order`: 수량 유효성(`InvalidStateError`) → 시료 존재 확인(`sample_repo.get`, 없으면 `NotFoundError`) → Repository에 위임하는 순서로 검증
- PoC는 `Order.id`를 `int`로 두고 Repository가 자동 증가시키지만, 본 프로젝트는 Phase 0에서 이미 `order_id: str` + JSON 스키마(`O001` 형식)로 설계했으므로 이 방식을 유지하고, ID 생성은 Controller에서 순번 기반 문자열로 생성
- 테스트 케이스 구성(정상 생성/존재하지 않는 시료/수량 0 이하/ID 증가/상태별 필터링)을 참고하되, "상태별 필터링"은 Phase 3(승인/거절)에서 실제로 쓰이므로 이번 Phase 범위에서는 제외

## 2. Phase 0/1 대비 변경 사항

- 없음. 기존 `Order` 모델(`order_id`, `sample_id`, `customer_name`, `quantity`, `status`, `created_at`), `OrderRepository`(Phase 0에서 구현된 범용 CRUD)를 그대로 사용

## 3. 신규 파일

```
src/sample_order_system/
├── controllers/
│   └── order_controller.py   # (신규) 주문 접수 유스케이스
├── views/
│   └── order_view.py         # (신규) 순수 포맷팅 함수
tests/
├── controllers/test_order_controller.py   # (신규)
└── views/test_order_view.py               # (신규)
```

## 4. 설계 상세

### `OrderController`
- `__init__(self, sample_repo: SampleRepository, order_repo: OrderRepository, clock=lambda: datetime.now().isoformat())`
  - `clock`은 테스트에서 결정적인 시각 주입을 위한 선택적 의존성 (기본값: 현재 시각)
- `place_order(sample_id: str, customer_name: str, quantity: int) -> Order`
  1. `quantity <= 0` → `ValidationError`
  2. `self._sample_repo.get(sample_id)` 호출로 존재 확인 (없으면 `NotFoundError`가 그대로 전파)
  3. `order_id` 생성: 기존 주문 개수를 기준으로 `f"O{len(existing)+1:03d}"` 형식 순번 부여 (예: `O001`, `O002`, ...)
  4. `Order(order_id=..., sample_id=sample_id, customer_name=customer_name, quantity=quantity, status=OrderStatus.RESERVED, created_at=self._clock())` 생성 후 `order_repo.add()`로 저장, 생성된 `Order` 반환

### `views/order_view.py`
- `format_order_registration_success(order: Order) -> str`: 주문ID/시료ID/고객명/수량/상태 포함

## 5. TDD 테스트 케이스

**`OrderController`**
- 정상 접수: 존재하는 시료ID로 주문 시 `RESERVED` 상태의 `Order` 반환, 저장소에 반영됨
- 존재하지 않는 시료 ID → `NotFoundError`
- 수량 0 또는 음수 → `ValidationError`
- 연속 접수 시 `order_id`가 겹치지 않고 순번대로 증가 (`O001`, `O002`)
- 주입한 `clock`으로 `created_at`이 그대로 반영되는지

**`order_view`**
- `format_order_registration_success`: 주문ID/고객명/수량 등 주요 필드가 출력 문자열에 포함되는지

## 6. 완료 기준

- 위 테스트가 모두 통과
- 전체 `pytest` 통과 (Phase 0/1 회귀 포함)
- `reports/phase2.md` 작성 후 사용자 확인
