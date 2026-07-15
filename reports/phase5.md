# Phase 5. 출고 처리 — 완료 보고서

계획 문서: `plans/phase5.md`

## 요약

Phase 5의 계획 항목(CONFIRMED 주문 출고 처리)을 TDD로 구현 완료했습니다. 테스트 86개 전부 통과했으며, 계획 대비 범위 변경은 없습니다.

## 구현 항목

| 영역 | 파일 | 내용 |
|---|---|---|
| Controller | `controllers/shipment_controller.py` | `release(order_id)` — `CONFIRMED`가 아니면 `InvalidStateTransitionError`, 맞으면 `RELEASE`로 전환 후 저장 |
| View | `views/shipment_view.py` | `format_release_result` — `input()` 없는 순수 포맷팅 함수 |

## 테스트 결과

```
86 passed in 0.86s
```

- `tests/controllers/test_shipment_controller.py` (4): `CONFIRMED` 주문 정상 출고, `RESERVED`/`PRODUCING` 주문 출고 시도 시 예외, 이미 `RELEASE`된 주문 재출고 시도 시 예외(중복 방지)
- `tests/views/test_shipment_view.py` (1): 주문ID/상태가 출력 문자열에 포함되는지 검증

## 계획 대비 차이

- 없음. PoC(`ConsoleMVC`)의 `ShipmentController` 패턴을 그대로 적용

## 커밋 이력

```
c1adc21 feat: ShipmentController 구현 (출고 처리)
b6a2d19 feat: shipment_view 순수 포맷팅 함수 구현
```

## 다음 단계

Phase 6(통합 및 마무리) 상세 계획 작성 → 리뷰 → TDD 구현
