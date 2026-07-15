# Phase 3. 주문 승인/거절 및 생산 라인 — 완료 보고서

계획 문서: `plans/phase3.md`

## 요약

Phase 3의 계획 항목(승인/거절, 생산 라인 FIFO/턴 진행)을 TDD로 구현 완료했습니다. 테스트 69개 전부 통과했으며, 계획에서 사전 확인한 설계 결정(초과 생산분 재고 반영)을 그대로 적용했습니다.

## 구현 항목

| 영역 | 파일 | 내용 |
|---|---|---|
| 모델 | `models/production_queue.py` | `ProductionQueueEntry`에 `shortfall` 필드 추가 (완료 시 초과분 계산용) |
| Repository | `repository/production_queue_repository.py` | `id_field="order_id"`, FIFO 순서는 리스트 삽입 순서로 유지 |
| Controller | `controllers/approval_controller.py` | `approve()`: 재고 충분 시 즉시 `CONFIRMED`(재고 차감), 부족 시 `shortfall` 계산 → `ceil(shortfall/yield_rate)`로 실 생산량, `ceil(avg_production_time * 실생산량)`으로 정수 턴 수 산출 후 생산 큐 등록, `PRODUCING` 전환. `reject()`: `RESERVED`가 아니면 `InvalidStateTransitionError` |
| Controller | `controllers/production_controller.py` | `advance_turns(turns)`: FIFO 큐 맨 앞부터 턴 소모, 완료 시 스필오버로 다음 작업 이어서 처리(한 번의 호출로 여러 작업 완료 가능), 완료 시 초과분(`actual_production_qty - shortfall`)을 재고에 가산하고 주문 `CONFIRMED` 전환. `current_job()`/`waiting_jobs()`로 큐 조회 |
| View | `views/approval_view.py`, `views/production_view.py` | 승인/거절 결과, 현재/대기 작업, 턴 진행 결과 포맷팅 (순수 함수) |

## 설계 결정 반영

- **턴 수 정수화**: `total_production_turns = ceil(avg_production_time * actual_production_qty)` — PoC의 float(분) 모델과 달리 턴 기반 정수로 관리
- **초과 생산분 재고 반영**: 사전 확인받은 대로, 생산 완료 시 `actual_production_qty - shortfall`만큼을 재고에 가산 (PoC는 이를 폐기하나, 본 프로젝트는 재고 정합성을 위해 반영)

## 테스트 결과

```
69 passed in 0.51s
```

- `tests/models/test_models.py`: `shortfall` 필드 반영 회귀
- `tests/repository/test_production_queue_repository.py` (3): FIFO 순서 유지, 삭제, 존재하지 않는 ID 예외
- `tests/controllers/test_approval_controller.py` (6): 재고 충분/부족 분기, `ceil` 계산 검증(10/0.4=25, 3.0*25=75), 상태 전이 예외(승인/거절 각각)
- `tests/controllers/test_production_controller.py` (6): 부분 진행, 정확한 완료(재고 반영 확인), 스필오버로 다건 완료, 현재/대기 작업 조회, 빈 큐 처리
- `tests/views/test_approval_view.py` (2), `tests/views/test_production_view.py` (5): 포맷팅 함수의 필드 포함 여부 및 빈 상태 안내 문구

## 계획 대비 차이

- 없음. `plans/phase3.md`에서 사전 확인받은 두 가지 설계 결정(턴 정수화, 초과분 재고 반영)을 포함해 계획대로 구현

## 커밋 이력

```
986a2ac refactor: ProductionQueueEntry에 shortfall 필드 추가
b4dcf37 feat: ProductionQueueRepository 구현
fd8aad0 feat: ApprovalController 구현 (승인/거절, 생산 라인 등록)
88718e6 feat: ProductionController 구현 (턴 진행, FIFO 완료 처리, 큐 조회)
a292261 feat: approval_view/production_view 순수 포맷팅 함수 구현
```

## 다음 단계

Phase 4(모니터링) 상세 계획 작성 → 리뷰 → TDD 구현
