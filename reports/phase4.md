# Phase 4. 모니터링 — 완료 보고서

계획 문서: `plans/phase4.md`

## 요약

Phase 4의 계획 항목(상태별 주문 집계, 시료별 재고 현황)을 TDD로 구현 완료했습니다. 테스트 81개 전부 통과했으며, 계획에서 사전 확인한 설계 결정(재고 판정 기준: 미결 주문 수요 대비)을 그대로 적용했습니다.

## 구현 항목

| 영역 | 파일 | 내용 |
|---|---|---|
| 모델 | `models/monitoring.py` | `StockStatus` DTO (`sample_id`, `name`, `quantity`, `status`, `remaining_ratio`) |
| Controller | `controllers/monitoring_controller.py` | `count_by_status()`: `RESERVED`/`PRODUCING`/`CONFIRMED`/`RELEASE` 집계(`REJECTED` 제외, 없는 상태도 0으로 표시). `stock_status()`: 시료별 재고 대비 해당 시료의 `RESERVED` 주문 수량 합(수요)으로 여유/부족/고갈 및 잔여율 계산 |
| View | `views/monitoring_view.py` | `format_order_counts`, `format_stock_status_list` — 순수 포맷팅 함수 |

## 설계 결정 반영

- **재고 판정 기준**: 사전 확인받은 대로 미결(`RESERVED`) 주문 수요 대비 방식 채택
  - 재고 0 → `고갈`(잔여율 0%)
  - 수요 없음 → `여유`(잔여율 100%)
  - 수요 > 재고 → `부족`(잔여율 = 재고/수요*100)
  - 재고 ≥ 수요 → `여유`(잔여율 100% 캡)
  - 기존 스키마만으로 계산되어 신규 필드 추가 없음

## 테스트 결과

```
81 passed in 0.57s
```

- `tests/models/test_monitoring_models.py` (1): `StockStatus` 필드 검증
- `tests/controllers/test_monitoring_controller.py` (7): `REJECTED` 제외 및 상태별 정확한 집계, 주문 없을 때 전부 0, 재고 고갈/수요없음/부족/충족 4가지 판정 케이스, `CONFIRMED` 등 비-`RESERVED` 주문은 수요에 포함되지 않음 확인, 여러 시료 각각 반환
- `tests/views/test_monitoring_view.py` (3): 상태별 건수 포맷, 빈 목록 안내 문구, 필드 포함 여부

## 계획 대비 차이

- 없음. `plans/phase4.md`에서 사전 확인받은 재고 판정 기준(미결 주문 수요 대비)을 그대로 구현

## 커밋 이력

```
cfb8c3c feat: StockStatus 모델 추가
fc9dd1a feat: MonitoringController 구현 (상태별 집계, 재고 현황)
644e130 feat: monitoring_view 순수 포맷팅 함수 구현
```

## 다음 단계

Phase 5(출고 처리) 상세 계획 작성 → 리뷰 → TDD 구현
