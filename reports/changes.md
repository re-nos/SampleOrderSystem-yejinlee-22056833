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
