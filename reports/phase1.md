# Phase 1. 시료 관리 — 완료 보고서

계획 문서: `plans/phase1.md`

## 요약

Phase 1의 계획 항목(시료 등록/조회/검색 및 재고 연동)을 TDD로 구현 완료했습니다. 테스트 39개 전부 통과했으며, 계획 대비 범위 변경은 없습니다.

## 구현 항목

| 영역 | 파일 | 내용 |
|---|---|---|
| 모델 | `models/sample.py` | `avg_production_time`을 `int → float`로 변경, `SampleSummary`(시료+재고 조회 전용) 추가 |
| Repository | `repository/inventory_repository.py` | `InventoryRecord`용 `JsonRepository` 특화 구현 |
| Repository | `repository/sample_repository.py` | `search_by_name(keyword)` 추가 (대소문자 무시 부분일치) |
| Controller | `controllers/sample_controller.py` | `register_sample`(등록 시 재고 0 자동 초기화), `list_samples`, `search_by_name` — 조회 결과에 재고 수량 포함 |
| View | `views/sample_view.py` | `format_sample_list`, `format_registration_success` — `input()` 없는 순수 포맷팅 함수 |

## 테스트 결과

```
39 passed in 0.22s
```

- `tests/models/test_models.py`: `Sample`(float 타입 반영) + `SampleSummary` 필드 검증
- `tests/repository/test_inventory_repository.py` (3): CRUD, 존재하지 않는 ID 예외
- `tests/repository/test_sample_order_repositories.py`: 기존 CRUD + `search_by_name` 정상/결과없음 케이스 추가
- `tests/controllers/test_sample_controller.py` (5): 등록 시 재고 0 초기화, 중복 ID 예외, 재고 갱신 반영, 이름 검색 정상/결과없음
- `tests/views/test_sample_view.py` (3): 빈 목록 안내 문구, 필드 포함 여부, 등록 완료 메시지

## 계획 대비 차이

- 없음. `plans/phase1.md`에 정의된 설계(모델 변경, `InventoryRepository`, `SampleController`, `sample_view`)를 그대로 구현
- `views/`는 계획대로 순수 포맷팅 함수만 구현했고, `input()` 기반 콘솔 메뉴 루프는 Phase 6(`app.py`)에서 통합 예정

## 커밋 이력

```
1c518f0 refactor: Sample.avg_production_time을 float으로 변경, SampleSummary 모델 추가
32b7124 feat: InventoryRepository 구현
6f8e772 feat: SampleRepository에 이름 검색(search_by_name) 기능 추가
3be9bb0 feat: SampleController 구현 (등록/조회/검색, 재고 초기화 연동)
07c60e7 feat: sample_view 순수 포맷팅 함수 구현
```

## 다음 단계

Phase 2(시료 주문 접수) 상세 계획 작성 → 리뷰 → TDD 구현
