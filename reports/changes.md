# 변경 요청 이력

Phase 단위 작업(`reports/phase{N}.md`) 외에, 사용자가 수시로 요청하는 변경 사항은 이 파일에 항목을 추가(append)하는 방식으로 기록합니다.

---

## 2026-07-15: 콘솔 UI 정렬/색상, 메뉴 복귀 확인, 턴 완료 메시지 조건부 출력

### 요청 내용
1. 콘솔 출력 레이아웃을 `ConsoleMVC` PoC를 참고해 정렬(align)하고 컬러 추가
2. 각 명령 처리 후 메인 메뉴로 자동으로 돌아가지 않고, "메뉴로 돌아가기"를 사용자가 확인(Enter)해야 돌아가도록 변경
3. 매 명령마다 "이번 턴에 완료된 생산 작업이 없습니다" 메시지를 출력하지 말고, 실제로 완료된 작업이 있을 때만 출력
4. (프로세스) 앞으로 변경 요청은 완료 후 이 파일에 append 방식으로 report 작성

### 변경 내용

| 영역 | 파일 | 내용 |
|---|---|---|
| 신규 유틸 | `views/colors.py` | `ConsoleMVC` PoC의 색상 팔레트 참고 (`colorize`, `order_status_color`, `stock_status_color`) |
| 신규 유틸 | `views/text_width.py` | 한글 전각 문자를 고려한 `display_width`/`pad` (PoC와 동일 방식) |
| View 정렬/색상 | `sample_view.py`, `order_view.py`, `approval_view.py`, `production_view.py`, `monitoring_view.py`, `shipment_view.py` | 목록 출력에 `pad()` 기반 컬럼 정렬 적용, 주문/재고 상태 값에 `order_status_color`/`stock_status_color` 적용 |
| 앱 통합 | `app.py` | 메인 메뉴에 정렬/색상 적용(`_render_main_menu`, `_menu_row`). `run()` 루프에 `_wait_for_return_to_menu()` 추가 — 명령 처리 후 사용자가 Enter로 확인해야 메인 메뉴로 복귀 (단, 잘못된 메뉴 번호 선택 시에는 턴 진행/복귀 확인 없이 즉시 메인 메뉴로 돌아감, PoC와 동일). `_advance_turn()`이 완료된 작업이 있을 때만 결과를 출력하도록 변경 |

### 테스트 결과

```
121 passed
```

- 신규: `tests/views/test_colors.py`, `tests/views/test_text_width.py`
- 갱신: 각 view 테스트에 정렬/색상 검증 케이스 추가, `tests/test_app.py`의 입력 시나리오에 "메뉴로 돌아가기" 확인 입력 추가 및 잘못된 메뉴 선택 시 복귀 확인이 생략되는지, 턴 완료 메시지가 완료 시에만 뜨는지 검증하는 케이스 추가

### 수동 검증

`python -m sample_order_system.app`에 해당하는 흐름을 재현해 색상 코드(ANSI)와 컬럼 정렬, "[메뉴로 돌아가기] Enter 키를 누르세요..." 프롬프트, 완료된 생산이 없을 때 턴 메시지가 출력되지 않음을 확인

### 커밋 이력

```
04596fa feat: colors/text_width 유틸리티 추가 (콘솔 UI 색상/정렬 기반)
eb0b2a6 feat: sample_view에 정렬/색상 적용
1d21fac feat: order_view에 상태별 색상 적용
3d712bc feat: approval_view에 상태별 색상 적용
33f0573 feat: shipment_view에 상태별 색상 적용
1284ba0 feat: production_view에 색상 적용
3279a71 feat: monitoring_view에 정렬/색상 적용
8a4c48d feat: 콘솔 UI 정렬/색상 적용, 메뉴 복귀 확인 단계 추가, 턴 완료 메시지 조건부 출력
```

---

## 2026-07-15: 승인/거절 메뉴에 대기 목록 및 재고 확인 표시 추가

### 요청 내용
주문 승인/거절 메뉴에서 승인/거절 전에 승인 대기 중인 예약(RESERVED) 목록을 표로 출력하고, 승인/거절할 주문 ID를 입력하면 재고·주문 수량·부족분을 보여준 뒤 승인/거절을 선택하도록 변경.

### 변경 내용

| 영역 | 파일 | 내용 |
|---|---|---|
| 모델 | `models/stock_check.py` | `StockCheck` DTO (`order_id`, `sample_id`, `quantity`, `inventory_quantity`, `shortfall`) 신규 추가 |
| Controller | `controllers/approval_controller.py` | `list_pending_orders()` — `RESERVED` 상태 주문만 반환. `check_stock(order_id)` — 주문 수량/현재 재고/부족분(`max(0, 주문수량-재고)`) 계산 |
| View | `views/approval_view.py` | `format_pending_orders(orders)` — 대기 주문 표(정렬/상태색상 적용), `format_stock_check(check)` — 재고/주문수량/부족분 출력 |
| 앱 통합 | `app.py` | `_handle_approval()` 흐름을 "대기 목록 출력 → 주문 ID 입력 → 재고 확인 출력 → 승인/거절 선택"으로 변경 (기존 입력 개수는 그대로 유지: 주문 ID, 승인/거절 여부) |
| 버그 수정 | `views/approval_view.py` | 수동 검증 중 발견한 정렬 버그 수정 — "주문ID" 헤더 라벨이 컬럼 폭(6)과 같아 다음 컬럼과 붙어 보이던 문제, 폭을 8로 조정 |

### 테스트 결과

```
130 passed
```

- 신규: `tests/models/test_stock_check_model.py`, `ApprovalController.list_pending_orders`/`check_stock` 테스트, `approval_view.format_pending_orders`/`format_stock_check` 테스트(정렬 검증 포함)
- 갱신: `tests/test_app.py`에 승인 흐름에서 대기 목록·재고 확인 출력이 나타나는지 검증하는 assertion 추가 (입력 시나리오 자체는 변경 없음)

### 수동 검증

`python -m sample_order_system.app`에 해당하는 흐름을 재현해 승인 메뉴 진입 시 대기 주문 표가 먼저 출력되고, 주문 ID 입력 후 재고/주문수량/부족분이 표시된 다음 승인/거절을 선택하는 흐름을 확인. 이 과정에서 헤더 정렬 버그를 발견해 함께 수정.

### 커밋 이력

```
a9cfe9a feat: StockCheck 모델 추가
616218c feat: ApprovalController에 list_pending_orders/check_stock 추가
f7d76ca feat: approval_view에 대기 목록/재고 확인 출력 함수 추가
27b0de4 feat: 승인/거절 메뉴에 대기 목록 및 재고 확인 표시 통합
8a0c155 fix: 승인 대기 목록 표의 주문ID 컬럼 폭 정렬 버그 수정
```
