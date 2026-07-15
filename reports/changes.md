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

---

## 2026-07-15: 콘솔 UI를 UI_Console_Examples.md 예시에 맞춰 전면 개편

### 요청 내용
1. 색상은 유지한 상태에서 화면 UI를 `UI_Console_Examples.md`의 예시와 같이 변경
2. 더미 데이터도 예시와 같은 스타일로 변경
3. 예시 화면을 그대로 테스트하기 위한 전체 e2e 테스트 파일 작성

구현 전 4가지 설계 결정을 확인받음: 주문 ID 형식(`ORD-YYYYMMDD-NNNN`), 승인/출고 선택 방식(번호 선택), 주문 접수 확인 단계 추가, 생산라인 완료 예정 시각(현재시각+남은턴(분) 가상 계산).

### 변경 내용

| 영역 | 파일 | 내용 |
|---|---|---|
| 주문 ID | `controllers/order_controller.py` | `O001` → `ORD-{생성일자YYYYMMDD}-{순번4자리}` 형식으로 변경 |
| 모델 | `models/stock_check.py` | `actual_production_qty`/`total_production_turns` 프리뷰 필드 추가 |
| 모델 | `models/production_job_detail.py` (신규) | 생산 큐 항목 + 주문/시료 정보 결합 조회 전용 DTO |
| Controller | `controllers/approval_controller.py` | `list_pending_orders`/`check_stock`에 실생산량·소요턴 프리뷰 계산 추가(중복 로직은 `_estimate_production`으로 통합) |
| Controller | `controllers/shipment_controller.py` | `list_releasable_orders`(CONFIRMED 목록) 추가 |
| Controller | `controllers/sample_controller.py` | `get_summary`(단건 조회, 주문 확인 화면용) 추가 |
| Controller | `controllers/production_controller.py` | `sample_repo` 의존성 추가, `current_job_detail`/`waiting_job_details`(주문량/재고/부족/실생산량/수율 결합) 추가 |
| View | `views/sample_view.py` | "등록 시료 목록 (총 N종)" 제목, `ID`/`시료명`/`min/ea`/`ea` 단위 표기로 변경 |
| View | `views/monitoring_view.py` | 주문 현황을 RESERVED→CONFIRMED→PRODUCING(생산라인 대기 메모)→RELEASE 고정 순서로, 재고 표는 시료ID 열 제거하고 `ea`/정수 잔여율(%)로 변경 |
| View | `views/order_view.py` | `format_order_confirmation`(입력 내용 확인), `format_order_cancelled`(취소) 추가, 등록 성공 메시지를 "예약 접수 완료." 스타일로 변경 |
| View | `views/approval_view.py` | 대기 목록에 번호(`[N]`) 컬럼 추가, `format_stock_check`에 재고 부족/충분 여부에 따른 승인 확인 문구 + 실생산량/소요시간 표시 |
| View | `views/shipment_view.py` | `format_releasable_orders`(번호 선택 목록) 추가 |
| View | `views/production_view.py` | `format_current_job_detail`(진행률 %, 완료 예정 시각, 주문량/재고/부족/실생산량/수율), `format_waiting_job_details`(FIFO 순번 + 누적 완료 예정 시각) 추가 |
| 앱 통합 | `app.py` | 메인 메뉴에 시스템 현황판(등록 시료 종수/총 재고/전체 주문/생산라인 대기) 추가, 제목을 "반도체 시료 생산주문관리 시스템"으로 변경. 시료/모니터링 서브메뉴에 `[0] 뒤로` 추가. 주문 접수에 확인(Y/N) 단계 추가. 승인/출고를 번호 선택 방식으로 변경(`_select_by_number` 헬퍼 추가). 생산라인 조회를 상세 정보 기반으로 변경 |
| 더미 데이터 | `dummy_data.py` | 시료명을 예시와 같은 반도체 시료명 목록으로, 시료 ID를 `S-001` 형식으로, 주문 ID를 `ORD-` 형식으로, 재고/수율/생산시간 범위를 예시 스케일에 맞게 변경 |
| 정렬 버그 수정 | `approval_view.py`, `shipment_view.py`, `production_view.py` | 새 주문 ID 형식(18자)이 기존 컬럼 폭(14)보다 길어 다음 컬럼과 붙던 정렬 버그 발견 및 수정(폭 20으로 확대) |

### 신규 E2E 테스트

`tests/test_e2e_ui_examples.py` — 더미 데이터로 초기 상태를 구성한 뒤 예시의 7개 화면(메인 메뉴/시료 관리/시료 주문/승인·거절/모니터링/생산라인/출고)을 순서대로 콘솔 입력으로 재현하고, 각 화면의 핵심 레이블·단위·흐름(확인 단계, 번호 선택, 진행률, 완료 예정 시각 등)이 포함되는지 검증. 예시의 구체적인 수치는 더미 데이터에 따라 달라지므로 구조/문구 일치 여부를 검증하는 방식을 택함.

### 테스트 결과

```
155 passed
```

### 계획 대비 차이 / 단순화

- 시료 목록의 "...외 N종 [N] 다음페이지" 실시간 페이지네이션은 구현하지 않음(문서에서도 "자유롭게 조정 가능"이라 명시). 현재는 전체 목록을 한 번에 출력
- 예시의 정확한 시료명/재고량/주문번호는 재현하지 않고, 더미 데이터 생성기가 유사한 스타일(반도체 시료명, 단위, ID 형식)로 생성하도록 함

### 커밋 이력

```
ee07592 feat: 주문 ID 형식을 ORD-YYYYMMDD-NNNN으로 변경
4d930c5 feat: sample_view를 UI 예시 형식(단위/제목행)에 맞춰 변경
393242b feat: monitoring_view를 UI 예시 형식(정렬 순서/단위/생산라인 대기 메모)에 맞춰 변경
d17bba0 feat: StockCheck에 실생산량/소요턴 프리뷰 추가, approval_view를 번호 선택 UI로 변경
7d43e43 feat: ShipmentController에 list_releasable_orders 추가
659778a feat: shipment_view에 번호 선택 출고 목록 표시 추가
c74797c feat: SampleController에 get_summary 추가 (주문 확인 화면용)
ef0660b feat: order_view에 입력내용 확인/취소 화면 추가 (UI 예시 반영)
01ab774 feat: ProductionController에 current_job_detail/waiting_job_details 추가
16190a1 feat: production_view를 UI 예시 형식(진행률/완료예정시각/FIFO 표)으로 변경
b9ff17f feat: app.py를 UI 예시 흐름으로 전면 개편
0682e7d fix: 새 주문 ID 형식에 맞춰 표 컬럼 폭 정렬 버그 수정
74b41af feat: 더미 데이터를 UI 예시 스타일로 변경
5f10405 test: UI_Console_Examples.md 7개 화면을 재현하는 e2e 테스트 추가
```
