# Phase 3. 주문 승인/거절 및 생산 라인 — 상세 계획

`PLAN.md`의 Phase 3 항목을 구체화한 문서입니다. 이번 Phase는 범위가 크고 PoC와 다른 설계 판단이 필요한 지점이 있어, **섹션 2의 설계 결정 사항**을 먼저 확인해 주세요.

## 1. PoC 리뷰 요약 (`ConsoleMVC-yejinlee-22056833`)

- `controllers/approval_controller.py`: `approve()`(재고 비교 → 즉시 `CONFIRMED` 또는 `ProductionJob` 생성 후 `PRODUCING`), `reject()`(`RESERVED`가 아니면 `InvalidStateError`), `advance_production(minutes)`(생산 라인 tick → 완료된 주문 `CONFIRMED` 전환)
- `models/production.py`: `ProductionJob.create()`가 `quantity_to_produce = ceil(shortfall / yield_rate)`, `total_time = avg_production_time * quantity_to_produce` 계산. `ProductionLine`은 `deque` 기반 FIFO + `tick(minutes)`로 시간 소모, 완료 시 다음 작업으로 넘어가며 잔여 시간을 이어서 소모(스필오버) 처리
- PoC는 **실시간(연속) 시간(minutes, float)** 모델이지만, 본 프로젝트는 이미 결정된 대로 **턴(정수) 기반**이므로 아래 설계 결정에서 이 차이를 turns 단위로 변환합니다
- PoC는 생산 완료 후 초과 생산량(부족분보다 많이 만들어진 몫)을 재고에 반영하지 않음 — 아래 설계 결정 2에서 본 프로젝트의 처리 방식을 명확히 함

## 2. 설계 결정 사항 (확인 필요)

**결정 1 — 턴 수 정수화**: `total_production_turns = ceil(avg_production_time * actual_production_qty)`로 올림하여 정수 턴 수로 관리합니다 (PoC는 float `minutes`를 그대로 사용하지만, 본 프로젝트는 턴 기반이므로 정수 변환 필요).

**결정 2 — 초과 생산량의 재고 반영**: `actual_production_qty(ceil로 인해 부족분보다 많을 수 있음) - shortfall(실제 필요했던 부족분)`만큼의 초과분을 생산 완료 시 재고에 더합니다. PoC는 이 초과분을 버리지만(재고 미반영), PRD의 "재고량 확인" 모니터링 취지상 실제 생산된 물량이 재고에 정확히 반영되는 것이 더 합리적이라 판단했습니다.
  - 이를 위해 `ProductionQueueEntry`에 `shortfall` 필드를 추가합니다 (Phase 0 모델 확장).

이 두 가지가 PoC와 다른 지점이므로, 승인 후 구현 전에 확인 부탁드립니다. (다른 방식을 원하시면 말씀해주세요.)

## 3. Phase 0~2 대비 변경 사항

- `models/production_queue.py`의 `ProductionQueueEntry`에 `shortfall: int` 필드 추가 (기존 `order_id`, `sample_id`, `actual_production_qty`, `total_production_turns`, `remaining_turns`에 추가)

## 4. 신규 파일

```
src/sample_order_system/
├── repository/
│   └── production_queue_repository.py   # (신규) id_field="order_id"
├── controllers/
│   ├── approval_controller.py           # (신규) approve/reject
│   └── production_controller.py         # (신규) advance_turns, current_job, waiting_jobs (조회 전용)
├── views/
│   ├── approval_view.py                 # (신규)
│   └── production_view.py               # (신규)
tests/
├── repository/test_production_queue_repository.py
├── controllers/test_approval_controller.py
├── controllers/test_production_controller.py
├── views/test_approval_view.py
└── views/test_production_view.py
```

## 5. 설계 상세

### `ApprovalController`
- `__init__(self, sample_repo, order_repo, inventory_repo, production_queue_repo)`
- `approve(order_id) -> Order`
  1. `order = order_repo.get(order_id)`; `status != RESERVED`면 `InvalidStateTransitionError`
  2. `inventory = inventory_repo.get(order.sample_id)`
  3. 재고 충분(`inventory.quantity >= order.quantity`): 재고 차감 후 `update`, `order.status = CONFIRMED`
  4. 재고 부족: `shortfall = order.quantity - inventory.quantity`, 재고 0으로 갱신, `sample = sample_repo.get(...)`로 `yield_rate`/`avg_production_time` 조회
     - `actual_production_qty = ceil(shortfall / yield_rate)`
     - `total_production_turns = ceil(avg_production_time * actual_production_qty)`
     - `ProductionQueueEntry(order_id, sample_id, shortfall, actual_production_qty, total_production_turns, remaining_turns=total_production_turns)`를 `production_queue_repo.add()`로 큐에 등록 (FIFO, append 순서 = 큐 순서)
     - `order.status = PRODUCING`
  5. `order_repo.update(order)` 후 반환
- `reject(order_id) -> Order`: `RESERVED`가 아니면 `InvalidStateTransitionError`, 아니면 `REJECTED`로 갱신 후 반환

### `ProductionController`
- `__init__(self, order_repo, inventory_repo, production_queue_repo)`
- `advance_turns(turns: int) -> list[Order]`: 큐 맨 앞부터 FIFO로 `turns`만큼 시간을 소모, 완료된 작업만큼 스필오버 처리(한 번 호출로 여러 작업 완료 가능)
  - 완료 시: 초과분(`actual_production_qty - shortfall`)을 재고에 가산, 대응 주문을 `CONFIRMED`로 전환, 큐에서 제거
  - 부분 진행 시: `remaining_turns`만 갱신하고 중단 (다음 작업으로 넘어가지 않음)
  - 완료된 `Order` 목록을 FIFO 순서로 반환
- `current_job() -> Optional[ProductionQueueEntry]`: 큐의 첫 항목 (없으면 `None`)
- `waiting_jobs() -> list[ProductionQueueEntry]`: 큐의 첫 항목을 제외한 나머지

### Views
- `approval_view.format_approval_result(order) -> str`: 승인/거절 결과 및 전환된 상태 표시
- `production_view.format_current_job(entry) -> str`, `format_waiting_jobs(entries) -> str`, `format_turn_advance_result(completed_orders) -> str`

## 6. TDD 테스트 케이스

**`ApprovalController`**
- 재고 충분 → 즉시 `CONFIRMED`, 재고 차감 반영
- 재고 부족 → `PRODUCING`, 재고 0, 큐에 올바른 `actual_production_qty`/`total_production_turns`(ceil 계산, PoC와 동일한 `ceil(10/0.4)=25` 케이스 포함) 등록
- `RESERVED`가 아닌 주문 승인/거절 시도 → `InvalidStateTransitionError` (각각)
- 정상 거절 → `REJECTED`

**`ProductionController`**
- 부분 진행: turns가 남은 시간보다 적으면 미완료, `remaining_turns`만 감소
- 정확히 완료: 남은 시간과 정확히 일치하는 turns → 완료, 주문 `CONFIRMED`, 재고에 초과분 반영
- 스필오버: 한 번의 `advance_turns` 호출로 여러 작업이 연쇄 완료되는 경우 검증
- `current_job`/`waiting_jobs` 조회 정확성

**Views**
- 각 포맷 함수가 핵심 필드를 포함하는지 검증

## 7. 완료 기준

- 위 테스트가 모두 통과
- 전체 `pytest` 통과 (Phase 0~2 회귀 포함)
- `reports/phase3.md` 작성 후 사용자 확인
